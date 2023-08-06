# $Id: __init__.py e0c34b8eafc9 2012/09/01 10:36:44 patrick $
"""LePrisme engine."""

import re
from os import walk, listdir, makedirs, remove, rmdir
from os.path import join, exists, splitext, dirname, basename, isdir, relpath
from os.path import normpath, getmtime, samefile, commonprefix
from shutil import copy, rmtree
from ConfigParser import ConfigParser
from imp import load_source
from lxml import etree
from zipfile import is_zipfile

from ...utils import _, copy_content, unzip, config_get, camel_case, make_id
from ...xml import load
from .publiset import Publiset
from .transform import Transform


# =============================================================================
class Engine(object):
    """Main class for LePrisme engine."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build
        self.output = None

        # Configuration
        name = join(build.path, 'Processor', 'leprisme.ini')
        if not exists(name):
            build.stopped(_('File "leprisme.ini" is missing.'))
            return
        self._config = ConfigParser({
            'here': dirname(name), 'fid': '{fid}', 'ocffile': '{ocffile}'})
        self._config.read(name)

        # Relax NG, scripts, publiset and transformation
        self.relaxngs = self._load_relaxngs()
        self.scripts = self._load_scripts()
        self._transform = Transform(self)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the engine."""
        if self.build.stopped():
            return

        # Initialization
        self.output = join(self.build.path, 'Output')
        subdir = self.build.processing['variables'].get('subdir')
        if not subdir:
            self._initialize()
        if self.build.stopped():
            return

        # Process each file
        files = self._file_list()
        if not len(files):
            self.build.stopped(_('nothing to do!'), 'a_error')
            return
        for count, name in enumerate(files):
            percent = max(100 * (count + 1) / (len(files) + 1), 1)
            self._process(percent, name)
            if self.build.stopped():
                break

        # Finalization
        if not subdir:
            self.output = join(self.build.path, 'Output')
            self.finalize()

    # -------------------------------------------------------------------------
    def config(self, section, option, default=None):
        """Retrieve a value from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, section, option, default)

    # -------------------------------------------------------------------------
    def finalize(self):
        """Finalization."""

        # Remove temporary files
        if not self.build.processing['variables'].get('keeptmp'):
            self._remove_temporary_files(self.output)

        # Run finalization script
        if 'finalization' in self.scripts:
            self.scripts['finalization'](self)

    # -------------------------------------------------------------------------
    def _load_relaxngs(self):
        """Load Relax NG.

        :return: (dictionary)
            A dictionary of :class:`lxml.etree.RelaxNG` objets.
        """
        relaxngs = {}
        if not self._config.has_section('RelaxNG'):
            return relaxngs

        for root, filename in self._config.items('RelaxNG'):
            if root not in ('here', 'fid', 'ocffile'):
                try:
                    relaxngs[root] = etree.RelaxNG(etree.parse(filename))
                except IOError, err:
                    self.build.stopped(err)
                    return
                except (etree.XMLSyntaxError, etree.RelaxNGParseError), err:
                    self.build.stopped('"%s": %s' % (filename, err))
                    return
        return relaxngs

    # -------------------------------------------------------------------------
    def _load_scripts(self):
        """Load script files.

        :return: (dictionary)
            A dictionary of script main functions.
         """
        scripts = {}
        for name in (('Initialization', 'script'),
                     ('Transformation', 'preprocess'),
                     ('Transformation', 'postprocess'),
                     ('Finalization', 'script')):
            # Find file
            filename = self.config(name[0], name[1])
            if not filename:
                continue
            if not exists(filename):
                self.build.stopped('Unknown file "%s"' % filename)
                return scripts

            # Load module
            module = load_source(splitext(basename(filename))[0], filename)
            scripts[name[0].lower() if name[1] == 'script' else name[1]] = \
                module.main
        return scripts

    # -------------------------------------------------------------------------
    def _update_output(self, filename, fid):
        """Compute output directory for file ``filename``.

        :param filename: (string)
            Relative path to the original file to transform.
        :param fid: (string)
            File ID.
        :return: (string)
            Output path.
        """
        subdir = self.build.processing['variables'].get('subdir')
        if subdir:
            filename = relpath(filename, commonprefix(tuple(
                self.build.pack['files']) + (filename,)))
            self.output = join(
                self.build.path, 'Output',
                subdir.replace('%(fid)s', camel_case(fid))
                .replace('%(path)s', dirname(filename)))
        else:
            self.output = join(self.build.path, 'Output')

    # -------------------------------------------------------------------------
    def _file_list(self):
        """List files in pack according to settings.

        :return: (list)
            File list.
        """
        regex = self._config.has_option('Input', 'file_regex') \
            and re.compile(self._config.get('Input', 'file_regex'))
        input_is_dir = self._config.has_option('Input', 'is_dir') \
            and self._config.get('Input', 'is_dir') == 'true'
        files = []

        for base in self.build.pack['files']:
            fullname = normpath(join(self.build.data_path, base))
            if not exists(fullname):
                self.build.stopped('Unknown file "%s"' % base, 'a_warn')
                continue

            if (not regex or regex.search(base)) \
                    and isdir(fullname) == input_is_dir:
                files.append(base)
            if not self.build.pack.get('recursive') or not isdir(fullname):
                continue

            for path, dirs, filenames in walk(fullname):
                names = input_is_dir and dirs or filenames
                for name in names:
                    if not regex or regex.search(name):
                        name = relpath(join(path, name), self.build.data_path)
                        name = isinstance(name, str) \
                            and unicode(name.decode('utf8')) or name
                        files.append(name)
        return files

    # -------------------------------------------------------------------------
    def _initialize(self, fid=None):
        """Initialization.

        :param fid: (string, optional)
            File ID.

        ``self.build.processing['templates']`` and
        ``self.build.pack['templates']`` are lists of tuples such as
        ``(<input_file>, <output_path>)``.
        """
        # Check
        if not self.output.startswith(self.build.path):
            self.build.stopped(_('file outside build directory'))
            return

        # Clean up
        if not exists(self.output):
            makedirs(self.output)
        fmt = self.config('Output', 'format')
        if fid and fmt and exists(join(self.output, fmt.format(fid=fid))):
            remove(join(self.output, fmt.format(fid=fid)))
        self._remove_temporary_files(
            self.output, fid and self._config.has_option('Input', 'unzip')
            and '%s~' % fid)

        # Create directories
        names = self.config('Initialization', 'directories', '')
        for name in names.split():
            if not exists(join(self.output, name)):
                makedirs(join(self.output, name))

        # Copy templates
        if not self._copy_templates():
            return

        # Run initialization script
        if 'initialization' in self.scripts:
            self.scripts['initialization'](self)

    # -------------------------------------------------------------------------
    def _process(self, percent, filename):
        """Process one XML file.

        :param percent: (integer)
            Percent of progress.
        :param filename: (string)
            Relative path of the file to process.
        """
        if self.build.stopped():
            return

        # Load path
        fid = make_id(
            splitext(basename(filename))[0],
            config_get(self._config, 'Output', 'make_id'))
        fullname = normpath(join(self.build.data_path, filename))
        self.build.log(u'%s ............' % fid, percent=percent)
        self._update_output(filename, fid)

        # Load folder
        if isdir(fullname):
            self._initialize(fid)
            self._transform.start(filename, fid, filename)
            return

        # Unzip file
        if self._config.has_option('Input', 'unzip') \
                and self._config.get('Input', 'unzip') \
                and is_zipfile(fullname):
            unzip(fullname, join(self.output, '%s~' % fid))
            fullname = join(
                self.output, '%s~' % fid, self._config.get('Input', 'unzip'))

        # Load file content
        data = self._file_content(fullname)
        if data is None:
            if self._config.has_option('Input', 'unzip') \
                    and isdir(join(self.output, '%s~' % fid)):
                rmdir(join(self.output, '%s~' % fid))
            self.build.stopped(_('"${f}" ignored', {'f': filename}), 'a_warn')
            return

        # Non Publiset file
        # pylint: disable = I0011, E1103
        if isinstance(data, basestring) or data.getroot().tag != 'publiset':
            self._initialize(fid)
            self._transform.start(filename, fid, data)
            return

        # Publiset selection
        publiset = Publiset(self, dirname(fullname))
        for set_root in data.findall('selection'):
            for file_elt in set_root.xpath('.//file'):
                name = relpath(publiset.fullname(file_elt),
                               self.build.data_path)
                if name != filename:
                    self._process(percent, name)
                if self.build.stopped():
                    return
            fid = set_root.get('id')
            self.build.log('%s ......' % fid)
            self._update_output(filename, fid)
            self._initialize(fid)
            self._transform.start(filename, fid, publiset.create(set_root))

        # Publiset composition
        for set_root in data.findall('composition'):
            fid = set_root.get('id')
            self.build.log(_('${f}: document composition', {'f': fid}))
            self._update_output(filename, fid)
            self._initialize(fid)
            self._transform.start(
                filename, fid, publiset.compose(filename, set_root))
            if self.build.stopped():
                return

    # -------------------------------------------------------------------------
    def _file_content(self, fullname):
        """Load file content.

        :param fullname: (string)
            Full path to file to load.
        :return: (string or :class:`lxml.etree.ElementTree` instance or
            ``None``)
        """
        # Content regex
        regex = self._config.has_option('Input', 'content_regex') \
            and self._config.get('Input', 'content_regex')

        # XML file
        if splitext(fullname)[1].lower() == '.xml':
            relaxngs = self.relaxngs \
                if self.config('Input', 'validate') == 'true' else None
            data = load(fullname, relaxngs)
            if isinstance(data, basestring):
                if regex and exists(fullname):
                    with open(fullname, 'r') as hdl:
                        data = re.search(regex, hdl.read()) and data
                self.build.stopped(data, 'a_error')
                return
            if not regex or re.search(regex, etree.tostring(data)):
                return data
        # Other
        elif exists(fullname):
            with open(fullname, 'r') as hdl:
                data = hdl.read()
            if not regex or re.search(regex, data):
                return data

    # -------------------------------------------------------------------------
    def _copy_templates(self):
        """Copy processor, processing and pack templates into ``output``
        directory.

        :return: (boolean)
        """
        # Copy template files from INI files
        names = self.config('Initialization', 'templates', '')
        for name in names.split():
            template = join(self.build.path, 'Processor', 'Templates', name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            path = self.config('template:%s' % name, 'path', '')
            copy_content(
                template, join(self.output, path), self._excluded_list(name))

        # Copy template files from processing and pack templates
        for name, path in self.build.processing['templates'] \
                + self.build.pack['templates']:
            template = join(self.build.data_path, name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            do_unzip = path[0:6] == 'unzip:'
            path = do_unzip and join(self.output, path[6:]) \
                or join(self.output, path)
            if isdir(template):
                copy_content(template, path)
            elif do_unzip and is_zipfile(template):
                unzip(template, path)
            else:
                if not exists(dirname(path)):
                    makedirs(dirname(path))
                copy(template, path)

        return True

    # -------------------------------------------------------------------------
    def _excluded_list(self, template):
        """Return exluded file list.

        :param template: (string)
            Template name.
        :return: (list)
        """
        exclude = []
        section = 'template:%s' % template
        if not self._config.has_section(section):
            return exclude

        for option in self._config.options(section):
            if option == 'exclude':
                exclude += self.config(section, option, '').split()
            elif option.startswith('exclude['):
                var_name = option[8:-1]
                if var_name[0] != '!' \
                        and self.build.processing['variables'].get(var_name):
                    exclude += self.config(section, option, '').split()
                elif var_name[0] == '!' and not \
                        self.build.processing['variables'].get(var_name[1:]):
                    exclude += self.config(section, option, '').split()

        return exclude

    # -------------------------------------------------------------------------
    def _remove_temporary_files(self, output, keep_dir=None):
        """Remove temporary files.

        :param output: (string)
            Full path to output directory.
        :param keep_dir: (string, optional)
            Name of directory to keep .
        """
        regex = self.config('Finalization', 'remove_regex', '~\.?\w{0,4}$')
        for path, dirs, files in walk(output, topdown=False):
            for name in dirs:
                if name != keep_dir and (
                        (regex and re.search(regex, name))
                        or not listdir(join(path, name))):
                    rmtree(join(path, name))
            for name in files:
                if regex and re.search(regex, name):
                    remove(join(path, name))

        if not samefile(output, join(self.build.path, 'Output')) \
                and not listdir(output):
            rmdir(output)
