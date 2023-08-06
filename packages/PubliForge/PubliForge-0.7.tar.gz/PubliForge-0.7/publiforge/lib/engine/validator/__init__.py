# $Id: __init__.py 77a5c869abcc 2012/09/02 18:01:52 patrick $
"""Validation engine."""

from os import walk
from os.path import join, exists, dirname, basename, isdir
from ConfigParser import ConfigParser
from lxml import etree
import re

from ...utils import _
from ...xml import load


# =============================================================================
class Engine(object):
    """Main class for Validator engine."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build

        # Configuration
        name = join(build.path, 'Processor', 'validator.ini')
        if not exists(name):
            build.stopped(_('File "validator.ini" is missing.'))
            return
        config = ConfigParser({'here': dirname(name)})
        config.read(name)
        if not config.has_section('RelaxNG'):
            build.stopped(_('Section [RelaxNG] is missing.'))
            return

        # Relax NG
        self._relaxngs = {}
        for root, name in config.items('RelaxNG'):
            if root == 'here':
                continue
            try:
                self._relaxngs[root] = etree.RelaxNG(etree.parse(name))
            except IOError, error:
                self.build.stopped(error)
                return
            except (etree.XMLSyntaxError, etree.RelaxNGParseError), error:
                self.build.stopped('"%s": %s' % (name, error))
                return
        if len(self._relaxngs) == 0:
            build.stopped(_('No Relax NG.'))
            return

        # File selection
        self._file_regex = config.has_option('Input', 'file_regex') \
            and re.compile(config.get('Input', 'file_regex')) \
            or re.compile(r'\.xml$')
        self._content_regex = config.has_option('Input', 'content_regex') \
            and re.compile(config.get('Input', 'content_regex'))

    # -------------------------------------------------------------------------
    def start(self):
        """Start the engine."""
        if self.build.stopped():
            return

        # Get file list
        file_list = []
        for name in self.build.pack['files']:
            fullname = join(self.build.data_path, name)
            if not exists(fullname):
                self.build.stopped('Unknown file "%s"' % name, 'a_warn')
                continue
            if isdir(fullname):
                for path, name, files in walk(fullname):
                    for name in files:
                        if not self._file_regex.search(name):
                            continue
                        name = join(path, name)
                        name = isinstance(name, str) \
                            and unicode(name.decode('utf8')) or name
                        file_list.append(name)
            elif self._file_regex.search(name):
                file_list.append(fullname)
        if not len(file_list):
            self.build.stopped(_('nothing to do!'), 'a_error')
            return

        # Validate
        for count, name in enumerate(file_list):
            percent = 100 * (count + 1) / (len(file_list) + 1)
            self._validate(percent, name)

    # -------------------------------------------------------------------------
    def _validate(self, percent, filename):
        """Validate one XML file.

        :param percent: (integer)
            Percent of progress.
        :param filename: (string)
            Absolute path of the file to validate.
        """
        with open(filename, 'r') as hdl:
            data = hdl.read()
        if self._content_regex and not self._content_regex.search(data):
            return
        self.build.log(
            u'%s ............' % basename(filename), 'a_build', percent)
        data = load(filename, self._relaxngs, data)
        if not isinstance(data, basestring):
            return
        if not 'values' in self.build.result:
            self.build.result['values'] = []
        self.build.result['values'].append(data)
        self.build.stopped(data)
