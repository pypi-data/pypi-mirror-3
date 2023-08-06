# $Id: transform.py 816eec7f0a0c 2012/03/22 10:22:19 patrick $
"""XML Transformation via XSL stylesheet."""

from os import walk, remove
from os.path import exists, join, dirname, relpath, getmtime, commonprefix
from lxml import etree
import re
import fnmatch

from ...utils import _, camel_case
from ...xml import load
from . import containers
from .iniscript import IniScript


# =============================================================================
class Transform(object):
    """Class for XML transformation."""
    # pylint: disable = I0011, E1103, R0902

    # -------------------------------------------------------------------------
    def __init__(self, engine):
        """Constructor method.

        :param engine: (:class:`~.lib.engine.leprisme.Engine` instance)
            Engine object on which it depends.
        """
        self._engine = engine
        self.fid = None
        self.data = None
        self.output = None

        # Load regex and XSL
        self._regex = self._load_regex()
        self._xslt = self._load_xslt()

        # List container factories
        self._factories = {
            'Zip': containers.ZipFactory(engine),
            'OCF': containers.OcfFactory(engine)}

        # INI script
        self._iniscript = IniScript(engine)

    # -------------------------------------------------------------------------
    def start(self, filename, fid, data, mtime=None):
        """Start the transformation.

        :param filename: (string)
            Relative path to the original file to transform.
        :param fid: (string)
            File ID.
        :param data: (string or :class:`lxml.etree.ElementTree` instance)
            Name of file or tree to transform.
        :param mtime: (timestamp, optional)
            Time of last modification of the source file.
        """
        # pylint: disable = I0011, R0911
        # Initialization
        if data is None or self._engine.build.stopped():
            return
        self.fid = fid
        self.data = data
        self.output = self._initialize(filename, mtime)
        if self.output is None or self._engine.build.stopped():
            return
        self._save_tmp(0)

        # Preprocess
        self._script_transform('preprocess', filename)
        if self.data is None or self._engine.build.stopped():
            return

        # Pre regex transformation
        self._regex_transform('preregex')
        if self.data is None or self._engine.build.stopped():
            return

        # XSL transformation
        self._xsl_transform(self._engine.build.processing['variables'])
        if self.data is None or self._engine.build.stopped():
            return

        # Generated INI files
        self._ini_scripts(filename)
        if self._engine.build.stopped():
            return

        # Post regex transformation
        self._regex_transform('postregex')
        if self.data is None or self._engine.build.stopped():
            return

        # Postprocess
        self._script_transform('postprocess', filename)

        # Finalize
        self._finalize()

    # -------------------------------------------------------------------------
    def _load_regex(self):
        """Load regular expressions from file.

        :return: (dictionary)
            A dictionary of 2 list of regular expressions.
        """
        regex = {}
        for kind in ('preregex', 'postregex'):
            # Load file
            name = self._engine.config('Transformation', kind)
            if not name:
                continue
            if not exists(name):
                self._engine.build.stopped(
                    'Unknown file "%s".' % name)
                return regex

            # Browse file
            regex[kind] = []
            for line in open(name, 'r'):
                line = line.strip()
                if line and not line[0] == '#' and not line[0:7] == '[Regex]':
                    line = line.partition(' =')
                    repl = line[2].strip()
                    if repl and repl[0] in '\'"' and repl[-1] in '\'"':
                        repl = repl[1:-1]
                    if repl.startswith('lambda'):
                        repl = eval(repl)
                    regex[kind].append(
                        (re.compile(line[0].strip(), re.MULTILINE), repl))
        return regex

    # -------------------------------------------------------------------------
    def _load_xslt(self):
        """Load XSL file and create a etree.XSLT object.

        :return: (:class:`lxml.etree.XSLT` instance)
        """
        filename = self._engine.config('Transformation', 'xsl')
        if not filename:
            return

        try:
            _xslt = etree.XSLT(etree.parse(filename))
        except (IOError, etree.XSLTParseError, etree.XMLSyntaxError), err:
            self._engine.build.stopped(
                str(err).replace(self._engine.build.path, '..'))
            return
        return _xslt

    # -------------------------------------------------------------------------
    def _initialize(self, name, mtime=None):
        """Prepare output directory and compute target name.

        :param name: (string)
            Relative path to file to transform.
        :param mtime: (timestamp, optinal)
            Time of last modification of the source file.
        :return: (string)
            Full path to output directory.
        """
        # Output path
        subdir = self._engine.build.processing['variables'].get('subdir')
        if subdir:
            name = relpath(name, commonprefix(tuple(
                self._engine.build.pack['files']) + (name,)))
            output = subdir.replace('%(fid)s', camel_case(self.fid))\
                     .replace('%(path)s', dirname(name))
            output = join(self._engine.build.path, 'Output', output)
        else:
            output = join(self._engine.build.path, 'Output')

        # Already processed?
        target = self._engine.config('Output', 'format')
        if target:
            target = join(output, target.format(fid=self.fid))
            if mtime is not None and \
                   not self._engine.build.processing['variables'].get('force')\
                   and exists(target) and getmtime(target) > mtime:
                if not 'files' in self._engine.build.result:
                    self._engine.build.result['files'] = []
                self._engine.build.result['files'].append(relpath(
                    target, join(self._engine.build.path, 'Output')))
                self._engine.build.log(
                    _('${f}: Already processed', {'f': self.fid}))
                return
            if exists(target):
                remove(target)

        # Initialize subdirectory
        if subdir:
            self._engine.initialize(output)

        return output

    # -------------------------------------------------------------------------
    def _script_transform(self, kind, filename):
        """Customized script transformation.

        :param kind: ('preprocess' or 'postprocess')
            Kind of regular expressions.
        :param filename: (string)
            Relative path to file to transform.
        """
        if not kind in self._engine.scripts:
            return
        message = {
            'preprocess': _('${f}: preprocess', {'f': self.fid}),
            'postprocess': _('${f}: post process', {'f': self.fid})}\
            .get(kind, '%s: %s' % (self.fid, kind))
        self._engine.build.log(
            message, 'a_build', self._engine.build.result['log'][-1][2])
        self.data = self._engine.scripts[kind](
            self._engine, filename, self.fid, self.data, self.output)
        if self.data is not None:
            self._save_tmp(1 if kind == 'preprocess' else 5)

    # -------------------------------------------------------------------------
    def _regex_transform(self, kind):
        """Regular expression transformation.

        :param kind: ('preregex' or 'postregex')
            Kind of regular expressions.
        :return: (string)
            Modified data or ``None`` if fails.
        """
        if not kind in self._regex:
            return
        message = {
            'preregex': _('${f}: pre-regex', {'f': self.fid}),
            'postregex': _('${f}: post regex', {'f': self.fid})}\
            .get(kind, '%s: %s' % (self.fid, kind))
        self._engine.build.log(
            message, 'a_build', self._engine.build.result['log'][-1][2])

        # Eventually, convert data into string
        if not isinstance(self.data, basestring):
            method = self._engine.config('Xslt', 'method', 'xml')
            if method in ('text', 'value') or self.data.getroot() is None:
                self.data = str(self.data)
            else:
                self.data = etree.tostring(self.data, method=method,
                    encoding='utf-8', xml_declaration=True, pretty_print=True)

        # Transform
        for regex in self._regex[kind]:
            self.data = regex[0].sub(regex[1], self.data)
        self._save_tmp(2 if kind == 'preregex' else 4)

    # -------------------------------------------------------------------------
    def _xsl_transform(self, variables):
        """XSL transformation.

        :param variables: (dictionary)
            Variable dictionary for XSL.
        """
        if self._xslt is None:
            return
        self._engine.build.log(
            _('${f}: XSL transformation', {'f': self.fid}),
            'a_build', self._engine.build.result['log'][-1][2])

        # Eventually, load XML
        if isinstance(self.data, basestring):
            relaxngs = self._engine.config('Input', 'validate') == 'true' and \
                       self._engine.relaxngs or None
            self.data = load(self.fid, relaxngs, self.data)
            if isinstance(self.data, basestring):
                self._engine.build.stopped(self.data, 'a_error')
                self.data = None
                return

        # Create params dictionary
        params = {}
        for name, value in variables.items():
            if isinstance(value, bool):
                params[name] = str(int(value))
            elif isinstance(value, int):
                params[name] = str(value)
            else:
                params[name] = '"%s"' % value

        # Transform
        # pylint: disable = I0011, W0142
        try:
            self.data = self._xslt(self.data,
                fid='"%s"' % self.fid, output='"%s/"' % self.output, **params)
        except etree.XSLTApplyError, err:
            self._engine.build.stopped(err)
            return

        # Clean xmlns=""
        if self.data.getroot() is not None:
            self.data = etree.tostring(self.data, method='xml',
                encoding='utf-8', pretty_print=True,
                xml_declaration=True).replace(' xmlns=""', '')
        for path, name, files in walk(self.output):
            for name in [join(path, k) for k in files
                         if k[-3:] in ('tml', 'opf', 'ncx')]:
                with open(name, 'r') as hdl:
                    content = hdl.read()
                with open(name, 'w') as hdl:
                    hdl.write(content.replace(' xmlns=""', ''))

        self._save_tmp(3)

    # -------------------------------------------------------------------------
    def _ini_scripts(self, filename):
        """Browse generated INI files and process them.

        :param filename: (string)
            Relative path to the original file to transform.
        """
        for path, name, files in walk(self.output):
            for name in fnmatch.filter(files, '%s-*~.ini' % self.fid):
                self._engine.build.log(_('${f}: script "${n}"',
                    {'f': self.fid, 'n': name[:-5]}),
                    'a_build', self._engine.build.result['log'][-1][2])
                self._iniscript.execute(
                    self.output, filename, join(path, name))
                if self._engine.build.stopped():
                    return

    # -------------------------------------------------------------------------
    def _save_tmp(self, suffix):
        """Save temporary data on file to debug.

        :param suffix: (string)
            Suffix for temporary file name.
        """
        if self._engine.build.processing['variables'].get('keeptmp'):
            fmt = '{fid}.data%d~.%s' % (
                suffix, 'txt' if isinstance(self.data, basestring) else 'xml')
            self._save_data(fmt)

    # -------------------------------------------------------------------------
    def _save_data(self, fmt):
        """Save data on file.

        :param fmt: (string)
            Target name format.
        :return: (string)
            Full path to saved file.
        """
        # Nothing to save
        method = self._engine.config('Xslt', 'method', 'xml')
        if self.data is None or not fmt or method == 'value':
            return
        filename = join(self.output, unicode(fmt).format(fid=self.fid))

        # Save string
        if isinstance(self.data, basestring):
            if not self.data.strip():
                return
            with open(filename, 'w') as hdl:
                hdl.write(self.data)
        # Save XML in text file
        elif method == 'text' or self.data.getroot() is None:
            if self.data.getroot() is not None:
                data = etree.tostring(
                    self.data, encoding='utf-8', pretty_print=True)
            else:
                data = re.sub(r'^<\?xml [^>]*>\s*', '', str(self.data))
            if not data.strip():
                return
            with open(filename, 'w') as hdl:
                hdl.write(data)
        # Save XML/HTML file
        else:
            try:
                self.data.write(filename, method=method, encoding='utf-8',
                                xml_declaration=True, pretty_print=True)
            except (ValueError, AssertionError), err:
                self._engine.build.stopped(err, 'a_error')
                return

        return filename

    # -------------------------------------------------------------------------
    def _finalize(self):
        """Finalization."""
        # Save file
        fmt = self._engine.config('Output', 'format')
        filename = \
            self._save_data(fmt) or join(self.output, fmt.format(fid=self.fid))
        if not exists(filename):
            filename = None

        # Validation
        if filename is not None and self._engine.relaxngs is not None \
               and self._engine.config('Output', 'validate') == 'true':
            self.data = load(filename, self._engine.relaxngs, self.data)
            if isinstance(self.data, basestring):
                self._engine.build.stopped(self.data, 'a_error')
                remove(filename)
                return

        # Container
        container = self._engine.config('Output', 'container') or \
            (self._engine.build.processing['variables'].get('zip') and 'Zip') \
            or None
        if container is not None:
            if container not in self._factories:
                self._engine.build.stopped(
                    _('Unknown container "${c}"', {'c': container}))
                return
            self._engine.build.log(
                _('${f}: container ${c}', {'f': self.fid, 'c': container}),
                'a_build', self._engine.build.result['log'][-1][2])
            filename = self._factories[container].make(self.fid, self.output)
            if not filename:
                return

        # Main finalization
        if self._engine.build.processing['variables'].get('subdir'):
            self._engine.finalize(self.output)

        # Filename in result
        if not self._engine.build.stopped():
            if filename is not None:
                if not 'files' in self._engine.build.result:
                    self._engine.build.result['files'] = []
                self._engine.build.result['files'].append(
                    relpath(filename, join(self._engine.build.path, 'Output')))
            elif isinstance(self.data, basestring):
                if not 'values' in self._engine.build.result:
                    self._engine.build.result['values'] = []
                self._engine.build.result['values'].append(self.data)
