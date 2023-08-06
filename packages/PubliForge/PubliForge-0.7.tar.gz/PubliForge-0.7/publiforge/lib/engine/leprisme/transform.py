# $Id: transform.py e0c34b8eafc9 2012/09/01 10:36:44 patrick $
"""XML Transformation via XSL stylesheet."""

from os import walk, remove, makedirs
from os.path import exists, join, dirname, relpath, splitext
from lxml import etree
import re
import fnmatch

from ...utils import _, camel_case, make_id
from ...xml import load
from . import containers
from .iniscript import IniScript


PF_NAMESPACE = 'http://publiforge.org/functions'


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

        # Load regex and XSL
        self._regex = self._load_regex()
        self._xslt = self._load_xslt()
        self._xml_decl = None
        namespace = etree.FunctionNamespace(PF_NAMESPACE)
        namespace['camel_case'] = _xpath_function_camel_case
        namespace['make_id'] = _xpath_function_make_id

        # List container factories
        self._factories = {
            'Zip': containers.ZipFactory(engine),
            'OCF': containers.OcfFactory(engine)}

        # INI script
        self._iniscript = IniScript(engine)

    # -------------------------------------------------------------------------
    def start(self, filename, fid, data):
        """Start the transformation.

        :param filename: (string)
            Relative path to the original file to transform.
        :param fid: (string)
            File ID.
        :param data: (string or :class:`lxml.etree.ElementTree` instance)
            Name of file or tree to transform.
        """
        # pylint: disable = I0011, R0911
        # Initialization
        if data is None or self._engine.build.stopped():
            return
        self.fid = fid
        self.data = data
        self._save_tmp(0)

        # Preprocess
        self._script_transform('preprocess', filename)

        # Pre regex transformation
        self._regex_transform('preregex')

        # XSL transformation
        self._xsl_transform(self._engine.build.processing['variables'])

        # INI files execution
        self._media_iniscripts(filename)

        # Post regex transformation
        self._regex_transform('postregex')

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
                if line and not line[0] == '#' and not line[0:7] == '[Regex]':
                    pattern, replace = line.partition(' =')[::2]
                    pattern = pattern.strip().decode('utf8')
                    if not pattern:
                        continue
                    if pattern[0] in '\'"' and pattern[-1] in '\'"':
                        pattern = pattern[1:-1]
                    replace = replace.strip().decode('utf8')
                    if replace and replace[0] in '\'"' \
                            and replace[-1] in '\'"':
                        replace = replace[1:-1]
                    if replace.startswith('lambda'):
                        replace = eval(replace)
                    regex[kind].append((re.compile(
                        pattern, re.MULTILINE | re.UNICODE), replace))
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
    def _script_transform(self, kind, filename):
        """Customized script transformation.

        :param kind: ('preprocess' or 'postprocess')
            Kind of regular expressions.
        :param filename: (string)
            Relative path to file to transform.
        """
        if not kind in self._engine.scripts or self.data is None \
                or self._engine.build.stopped():
            return
        message = {
            'preprocess': _('${f}: preprocess', {'f': self.fid}),
            'postprocess': _('${f}: post process', {'f': self.fid})}\
            .get(kind, '%s: %s' % (self.fid, kind))
        self._engine.build.log(message)
        self.data = self._engine.scripts[kind](
            self._engine, filename, self.fid, self.data)
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
        if not kind in self._regex or self.data is None \
                or self._engine.build.stopped():
            return
        message = {
            'preregex': _('${f}: pre-regex', {'f': self.fid}),
            'postregex': _('${f}: post regex', {'f': self.fid})}\
            .get(kind, '%s: %s' % (self.fid, kind))
        self._engine.build.log(message)

        # Eventually, convert data into string
        if not isinstance(self.data, basestring):
            self.data = etree.tostring(
                self.data, encoding='utf-8', xml_declaration=self._xml_decl,
                pretty_print=True)

        # Transform
        self.data = self.data.decode('utf8')
        for regex in self._regex[kind]:
            self.data = regex[0].sub(regex[1], self.data)
        self.data = self.data.encode('utf8')
        self._save_tmp(2 if kind == 'preregex' else 4)

    # -------------------------------------------------------------------------
    def _xsl_transform(self, variables):
        """XSL transformation.

        :param variables: (dictionary)
            Variable dictionary for XSL.
        """
        if self._xslt is None or self.data is None \
                or self._engine.build.stopped():
            return
        self._engine.build.log(_('${f}: XSL transformation', {'f': self.fid}))

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
        params = {
            'fid': '"%s"' % self.fid, 'output': '"%s/"' % self._engine.output,
            'processor':  '"%s/"' % join(self._engine.build.path, 'Processor')}
        for name, value in variables.items():
            if isinstance(value, bool):
                params[name] = str(int(value))
            elif isinstance(value, int):
                params[name] = str(value)
            else:
                params[name] = '"%s"' % value

        # Transform
        # pylint: disable = I0011, W0142
        if not exists(self._engine.output):
            makedirs(self._engine.output)
        try:
            self.data = self._xslt(self.data, **params)
        except etree.XSLTApplyError, err:
            self._engine.build.stopped(err)
            return
        self._xml_decl = '<?xml ' in str(self.data)
        self.data = (
            self.data.getroot() is not None
            and etree.ElementTree(self.data.getroot())) or str(self.data)

        # Clean xmlns=""
        if not isinstance(self.data, basestring):
            self.data = etree.tostring(
                self.data, encoding='utf-8', pretty_print=True,
                xml_declaration=self._xml_decl)
        self.data = self.data.replace(' xmlns=""', '')
        for path, name, files in walk(self._engine.output):
            for name in [join(path, k) for k in files
                         if k[-3:] in ('tml', 'opf', 'ncx', 'mil')]:
                with open(name, 'r') as hdl:
                    content = hdl.read()
                with open(name, 'w') as hdl:
                    hdl.write(content.replace(' xmlns=""', ''))

        self._save_tmp(3)

    # -------------------------------------------------------------------------
    def _media_iniscripts(self, filename):
        """Browse generated INI files for media and process them.

        :param filename: (string)
            Relative path to the original file to transform.
        """
        if self.data is None or self._engine.build.stopped():
            return
        for path, name, files in walk(self._engine.output):
            for name in fnmatch.filter(files, '%s-*~.ini' % self.fid):
                self._engine.build.log(
                    _('${f}: script "${n}"', {'f': self.fid, 'n': name[:-5]}))
                self._iniscript.convert_media(
                    self._engine.output, filename, join(path, name))
                if self._engine.build.stopped():
                    return

    # -------------------------------------------------------------------------
    def _post_iniscript(self, target_file):
        """Look for post INI script and process it.

        :param target_file: (string)
            Full path to target.
        """
        # Something to do?
        if target_file is None:
            return
        ini_file = '%s~.ini' % splitext(target_file)[0]
        if not exists(ini_file):
            return

        # Execution
        self._engine.build.log(_('${f}: post script', {'f': self.fid}))
        self._iniscript.post_execution(
            self._engine.output, ini_file, target_file)

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
        if self.data is None or not fmt:
            return

        # File name and directory
        filename = join(self._engine.output, unicode(fmt).format(fid=self.fid))
        if not exists(dirname(filename)):
            makedirs(dirname(filename))

        # Save string
        if isinstance(self.data, basestring):
            if not self.data.strip():
                return
            with open(filename, 'w') as hdl:
                hdl.write(self.data)
        # Save XML/HTML file
        else:
            try:
                self.data.write(
                    filename, encoding='utf-8', xml_declaration=self._xml_decl,
                    pretty_print=True)
            except (ValueError, AssertionError), err:
                self._engine.build.stopped(err, 'a_error')
                return

        return filename

    # -------------------------------------------------------------------------
    def _finalize(self):
        """Finalization."""
        # Save file
        fmt = self._engine.config('Output', 'format')
        filename = self._save_data(fmt) \
            or join(self._engine.output, fmt.format(fid=self.fid))
        if not exists(filename):
            filename = None

        # Post INI script
        self._post_iniscript(filename)

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
            filename = self._factories[container].make(
                self.fid, self._engine.output)
            if not filename:
                return

        # Main finalization
        if self._engine.build.processing['variables'].get('subdir'):
            self._engine.finalize()

        # Filename in result
        if not self._engine.build.stopped():
            if filename is not None:
                if not 'files' in self._engine.build.result:
                    self._engine.build.result['files'] = []
                self._engine.build.result['files'].append(
                    relpath(filename, join(self._engine.build.path, 'Output')))
            elif isinstance(self.data, basestring) and self.data.strip():
                if not 'values' in self._engine.build.result:
                    self._engine.build.result['values'] = []
                self._engine.build.result['values'].append(self.data)


# =============================================================================
def _xpath_function_camel_case(context, text):
    """XPath function:  camel_case()."""
    # pylint: disable = I0011, W0613
    return camel_case(text)


# =============================================================================
def _xpath_function_make_id(context, name, mode):
    """XPath function:  make_id()."""
    # pylint: disable = I0011, W0613
    return make_id(name, mode)
