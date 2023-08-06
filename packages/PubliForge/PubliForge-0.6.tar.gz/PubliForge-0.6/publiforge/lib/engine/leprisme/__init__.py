# $Id: __init__.py c24008cf2ab8 2012/06/02 16:20:06 patrick $
"""LePrisme engine."""

import re
from os import walk, listdir, makedirs, remove
from os.path import join, exists, splitext, dirname, basename, isdir, relpath
from os.path import getmtime
from shutil import copy, rmtree
from ConfigParser import ConfigParser
from imp import load_source
from lxml import etree
from zipfile import is_zipfile

from ...utils import _, copy_content, unzip, config_get
from ...xml import XML_NS, load
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
        subdir = self.build.processing['variables'].get('subdir', '') != ''
        output = join(self.build.path, 'Output')
        if not subdir:
            self.initialize(output)
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
            self.finalize(output)

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
    def initialize(self, output):
        """Initialization.

        :param output: (string)
            Full path to output directory.

        ``self.build.processing['templates']`` and
        ``self.build.pack['templates']`` are lists of tuples such as
        ``(<input_file>, <output_path>)``.
        """
        # Create directories
        if not exists(output):
            makedirs(output)
        self._remove_temporary_files(output)
        names = self.config('Initialization', 'directories', '')
        for name in names.split():
            if not exists(join(output, name)):
                makedirs(join(output, name))

        # Copy template files from INI files
        names = self.config('Initialization', 'templates', '')
        for name in names.split():
            path = self.config('template:%s' % name, 'path', '')
            copy_content(
                join(self.build.path, 'Processor', 'Templates', name),
                join(output, path), self._excluded_list(name))

        # Copy template files from processing and pack templates
        for name, path in self.build.processing['templates'] \
                + self.build.pack['templates']:
            name = join(self.build.data_path, name)
            do_unzip = path[0:6] == 'unzip:'
            path = do_unzip and join(output, path[6:]) or join(output, path)
            if isdir(name):
                copy_content(name, path)
            elif do_unzip and is_zipfile(name):
                unzip(name, path)
            else:
                if not exists(dirname(path)):
                    makedirs(dirname(path))
                copy(name, path)

        # Run initialization script
        if 'initialization' in self.scripts:
            self.scripts['initialization'](self, output)

    # -------------------------------------------------------------------------
    def finalize(self, output):
        """Finalization.

        :param output: (string)
            Full path to output directory.
        """
        # Remove temporary files
        if not self.build.processing['variables'].get('keeptmp'):
            self._remove_temporary_files(output)

        # Run finalization script
        if 'finalization' in self.scripts:
            self.scripts['finalization'](self, output)

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
            fullname = join(self.build.data_path, base)
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
        fid = splitext(basename(filename))[0]
        fullname = join(self.build.data_path, filename)
        self.build.log(u'%s ............' % fid, 'a_build', percent)

        # Load folder
        if isdir(fullname):
            self._transform.start(filename, fid, filename)
            return

        # Load file content
        data = self._file_content(fullname)
        if data is None:
            self.build.stopped(_('"${f}" ignored', {'f': filename}), 'a_warn')
            return

        # Non Publiset file
        # pylint: disable = I0011, E1103
        if isinstance(data, basestring) or data.getroot().tag != 'publiset':
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
            fid = set_root.get('%sid' % XML_NS)
            self.build.log('%s ............' % fid, 'a_build', percent)
            self._transform.start(filename, fid, publiset.create(set_root))

        # Publiset composition
        for set_root in data.findall('composition'):
            fid = set_root.get('%sid' % XML_NS)
            self.build.log(_('${f}: document composition', {'f': fid}))
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
                if regex:
                    with open(fullname, 'r') as hdl:
                        data = re.search(regex, hdl.read()) and data
                self.build.stopped(data, 'a_error')
                return
            if not regex or re.search(regex, etree.tostring(data)):
                return data
        # Other
        else:
            with open(fullname, 'r') as hdl:
                data = hdl.read()
            if not regex or re.search(regex, data):
                return data

    # -------------------------------------------------------------------------
    def _excluded_list(self, template):
        """Return exluded file list.

        :param template: (string)
            Template name.
        :return: (list)
        """
        exclude = []
        section = 'template:%s' % template
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
    def _remove_temporary_files(self, output):
        """Remove temporary files.

        :param output: (string)
            Full path to output directory.
        """
        regex = self.config('Finalization', 'remove_regex', '~\.?\w{0,4}$')
        for path, dirs, files in walk(output, topdown=False):
            for name in dirs:
                if (regex and re.search(regex, name)) \
                       or not listdir(join(path, name)):
                    rmtree(join(path, name))
            for name in files:
                if regex and re.search(regex, name):
                    remove(join(path, name))
