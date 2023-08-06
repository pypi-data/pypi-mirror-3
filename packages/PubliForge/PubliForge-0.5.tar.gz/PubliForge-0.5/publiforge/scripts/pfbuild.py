#!/usr/bin/env python
# $Id: pfbuild.py b1ffa5a75b89 2012/02/19 23:23:01 patrick $
"""Console script to build a processing."""

import sys
import logging
from os.path import exists, join, abspath, dirname, expanduser, relpath
from optparse import OptionParser
from lxml import etree
from locale import getdefaultlocale
from textwrap import fill
import re

from ..lib.utils import _, localizer
from ..lib.xml import XML_NS, load, local_text
from ..lib.build.agent import AgentBuildManager


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = OptionParser(
        'Usage: %prog [options] <build_file> [<file> <file>...]')
    parser.add_option('--list-processors', dest='list_processors',
        help='list available processors', default=False, action='store_true')
    parser.add_option('--list-variables', dest='list_variables',
        help='list variable values', default=False, action='store_true')
    parser.add_option('--show-variables', dest='show_variables', default=False,
        help='show variable parameters and values', action='store_true')
    parser.add_option('--loglevel', dest='log_level', help='log level',
        default='INFO')
    parser.add_option('--logfile', dest='log_file', help='log file')
    parser.add_option('--processor_root', dest='processor_root',
        help='processor path')
    parser.add_option('--storage_root', dest='storage_root',
        help='storage path')
    parser.add_option('--build_root', dest='build_root', help='build path')
    parser.add_option('--build_id', dest='build_id', help='build ID')
    parser.add_option('--recursive', dest='recursive',
        help='recursive parsing', default=False, action='store_true')
    opts, args = parser.parse_args()
    log_level = getattr(logging, opts.log_level.upper(), None)
    if len(args) < 1 or not exists(args[0]) or not log_level:
        parser.error('Incorrect argument')
        sys.exit(2)

    # Initialize log
    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    if opts.log_file:
        logging.basicConfig(filename=expanduser(opts.log_file), filemode='w',
                            level=log_level, format=logformat)
    else:
        logging.basicConfig(level=log_level, format=logformat)

    # Build
    BuildLauncher(opts).start(args[0], args[1:])


# =============================================================================
class BuildLauncher(object):
    """Class to launch a build on command-line."""

    # -------------------------------------------------------------------------
    def __init__(self, opts):
        """Constructor method."""
        self._opts = opts
        self._relaxngs = {'publiforge':
            join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}
        self._processor = None

    # -------------------------------------------------------------------------
    def start(self, build_file, files):
        """Start build.

        :param build_file: (string)
             Path to build XML file.
        :param files: (list)
             List of files on command-line.
        """
        # Load build file
        build_tree = load(build_file, self._relaxngs)
        if isinstance(build_tree, basestring):
            LOG.critical(self._translate(build_tree))
            return

        # Read settings
        settings = self._read_settings(build_file, build_tree)
        if settings is None:
            return

        # Create agent
        build_manager = AgentBuildManager(settings)
        build_manager.processor_list()
        if self._opts.processor_root:
            build_manager.add_processors(expanduser(self._opts.processor_root))

        # Read processing
        processing = self._read_processing(settings, build_manager, build_tree)
        if processing is None or self._list_processors(build_manager) \
               or self._display_variables(processing):
            return

        # Read pack
        pack = self._read_pack(settings, build_tree, files)
        if pack is None:
            return

        # Create a build and start it
        build_id = self._opts.build_id  \
                   or build_tree.find('build').get('%sid' % XML_NS)
        context = {'lang': getdefaultlocale()[0], 'local': True}
        build = build_manager.start_build(build_id, context, processing, pack)

        # Display result
        if build.result['status'] != 'a_end':
            return
        if 'a_error' in [k[1] for k in build.result['log']]:
            LOG.critical(self._translate(_('error occurred')))
            return
        if 'values' in build.result:
            for value in build.result['values']:
                LOG.info(self._translate(
                    _('Value = ${v}', {'v': value})))
        if 'files' in build.result:
            for name in build.result['files']:
                LOG.info(self._translate(_(
                    'File = ${n}', {'n': join(build.path, 'Output', name)})))

    # -------------------------------------------------------------------------
    def _list_processors(self, build_manager):
        """List available processors.

        :param build_manager: (:class:`~.lib.build.agent.AgentBuildManager`
            instance) Current build_manager objet.
        :return: (boolean)
            ``True`` if processors have been listed.
        """
        if not self._opts.list_processors:
            return False

        print '=' * 60
        print '{0:^60}'.format(self._translate(_('Processor list')))
        print '=' * 60

        lang = getdefaultlocale()[0]
        for processor_id in build_manager.processor_list():
            tree = load(join(build_manager.processor_path(processor_id),
                             'processor.xml'), self._relaxngs)
            if isinstance(tree, basestring):
                print u'[{0:<16}] !!! {1:}'.format(
                    processor_id, self._translate(tree))
                continue

            # pylint: disable = I0011, E1103
            print u'[{0:<16}] {1:}'.format(processor_id,
                local_text(tree, 'processor/label', lang=lang))

        return True

    # -------------------------------------------------------------------------
    def _display_variables(self, processing):
        """Display variable values and contraints.

        :param processing: (dictionary)
            Processing dictionary.
        :return: (boolean)
            ``True`` if variables have been displayed.
        """
        if not self._opts.list_variables and not self._opts.show_variables:
            return False

        fmt = u'  | {0:<11} : {1:}'
        lang = getdefaultlocale()[0]
        variables = processing['variables']
        for group in self._processor.find('processor/variables')\
                .iterchildren(tag=etree.Element):
            print '=' * 60
            print '{0:^60}'.format(local_text(group, 'label', lang=lang))
            print '=' * 60
            if self._opts.show_variables \
                   and group.find('description') is not None:
                print self._format_description(lang, group)
                print '-' * 60

            for var in group.findall('var'):
                var_type = var.get('type')
                value = variables.get(var.get('name'), '')
                print u'{0:} = {1:}'.format(var.get('name'), value)
                if not self._opts.show_variables:
                    continue
                print '  v'
                if var.findtext('default') is not None:
                    print fmt.format(self._translate(_('Default')),
                        var.findtext('default').strip())
                print fmt.format(self._translate(_('Type')), var_type)
                if var_type == 'regex':
                    print fmt.format(self._translate(_('Pattern')),
                        var.findtext('pattern').strip())
                elif var_type == 'select':
                    print fmt.format(self._translate(_('Options')),
                        ', '.join(['[%s] %s' % (k.get('value', k.text), k.text)
                                   for k in var.findall('option')]))
                if  var.find('description') is not None:
                    print fmt.format(self._translate(_('Description')),
                        self._format_description(lang, var, 18))
                print

        return True

    # -------------------------------------------------------------------------
    def _read_settings(self, build_file, build_tree):
        """Read settings from ``build_tree``.

        :param build_file: (string)
             Path to build XML file.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :return: (dictionary)
             A settings dictionary.
        """
        settings = {}
        element = build_tree.find('build/settings')
        for child in element.iterchildren(tag=etree.Element):
            key = child.get('key')
            if '.root' in key:
                settings[key] = abspath(
                    join(dirname(build_file), child.text.strip()))
            else:
                settings[key] = child.text.strip()

        if self._opts.storage_root:
            settings['storage.root'] = \
                expanduser(self._opts.storage_root)
        if self._opts.build_root:
            settings['build.root'] = expanduser(self._opts.build_root)

        if not settings['build.root']:
            LOG.critical(
                self._translate(_('Must have a directory for builds.')))
        if not 'processor.available' in settings:
            settings['processor.available'] = '*'

        return settings

    # -------------------------------------------------------------------------
    def _read_processing(self, settings, build_manager, build_tree):
        """Load processing structure from ``build_tree``.

        :param settings: (dictionary)
             Settings.
        :param build_manager: (:class:`~.lib.build.agent.AgentBuildManager`
            instance) Current build_manager objet.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :return: (dictionary)
             A processing structure or ``None`` if fails.
        """
        # Main structure
        root_elt = build_tree.find('build/processing')
        processing = {'processor_id': root_elt.findtext('processor').strip()}

        # Load processor
        # pylint: disable = I0011, E1103
        self._processor = build_manager.processor_path(
            processing['processor_id'])
        if self._processor is None:
            LOG.critical(self._translate(_('Unknown processor ${p}.',
                {'p': processing['processor_id']})))
            return
        self._processor = load(
            join(self._processor, 'processor.xml'), self._relaxngs)
        if isinstance(self._processor, basestring):
            LOG.critical(self._translate(self._processor))
            return

        # Variables
        processing['variables'] = self._read_variables(build_tree)
        if processing['variables'] is None:
            return

        # Resource files
        path = settings['storage.root']
        processing['resources'] = self._read_file_set(
            path, build_tree.find('build/processing/resources'))
        if processing['resources'] is None:
            return

        # Template files
        processing['templates'] = self._read_file_set(
            path, build_tree.find('build/processing/templates'))
        if processing['templates'] is None:
            return

        return processing

    # -------------------------------------------------------------------------
    def _read_pack(self, settings, build_tree, files):
        """Load pack structure from ``build_tree``.

        :param settings: (dictionary)
             Settings.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :param files: (list)
             List of files on command-line to process.
        :return: (dictionary)
             A pack structure or ``None`` if fails.
        """
        # Main structure
        pack = {'recursive': '0'}
        element = build_tree.find('build/pack')
        if element is not None and element.get('recursive') == 'true'\
               or self._opts.recursive:
            pack['recursive'] = '1'

        # Files
        path = settings['storage.root']
        pack['files'] = self._read_file_set(
            path, build_tree.find('build/pack/files'))
        if pack['files'] is None:
            return

        # Files from command-line
        for name in files:
            name = expanduser(name)
            if not exists(name):
                LOG.critical(self._translate(
                    _('Unknown file "${n}".', {'n': name})))
                return
            pack['files'].append(relpath(name, path))

        # Resource files
        pack['resources'] = self._read_file_set(
            path, build_tree.find('build/pack/resources'))
        if pack['resources'] is None:
            return

        # Template files
        pack['templates'] = self._read_file_set(
            path, build_tree.find('build/pack/templates'))
        if pack['templates'] is None:
            return

        return pack

    # -------------------------------------------------------------------------
    def _read_variables(self, build_tree):
        """Read variable definitions in processor tree and fill ``variables``
        dictionary.

        :param build_tree: (:class:`lxml.etree.ElementTree`)
             Build element tree.
        :return: (dictionary)
             Variable dictionary.
        """
        # pylint: disable = I0011, E1103
        variables = {}
        var = build_tree.find('build/processing/variables')
        values = dict([(k.get('name'), k.findtext('value') is not None
                        and k.findtext('value').strip() or '')
                       for k in var.findall('var')])

        for var in self._processor.findall('processor/variables/group/var'):
            name = var.get('name')
            error = self._translate(_('${v}: bad value.', {'v': name}))
            value = values[name] if name in values \
                    else var.findtext('default') is not None \
                    and var.findtext('default').strip() or ''

            if var.get('type') == 'boolean':
                if not value in ('true', 'false', '1', '0', ''):
                    LOG.critical(error)
                    return
                value = bool(value == 'true' or value == '1')
            elif var.get('type') == 'integer':
                if not value.isdigit():
                    LOG.critical(error)
                    return
                value = int(value)
            elif var.get('type') == 'select':
                if not value in [k.get('value') or k.text
                                 for k in var.findall('option')]:
                    LOG.critical(error)
                    return
                value = int(value) if value.isdigit() else value
            elif var.get('type') == 'regex':
                if not re.match(var.findtext('pattern').strip(), value):
                    LOG.critical(error)
                    return
                value = int(value) if value.isdigit() else value
            variables[name] = value

        return variables

    # -------------------------------------------------------------------------
    def _read_file_set(self, storage_root, element):
        """Read files from ``element``.

        :param storage_root: (string)
            Absolute root path to storages.
        :param element: (etree.Element object)
            ``templates`` XML element.
        :return: (list)
            A list of tuples such as ``(<input_file>, <output_path>)`` or
            ``None`` if fails.
        """
        set_list = []
        if element is None:
            return set_list

        for child in element.iterchildren(tag=etree.Element):
            name = child.text.strip()
            if not exists(join(storage_root, name)):
                LOG.critical(self._translate(
                    _('Unknown file "${n}".', {'n': name})))
                return
            if child.get('to'):
                set_list.append((name, child.get('to')))
            else:
                set_list.append(name)

        return set_list

    # -------------------------------------------------------------------------
    @classmethod
    def _format_description(cls, lang, root_elt, indent=0, width=60):
        """Return formatted description text.

        :param lang: (string)
            Preferred language.
        :param root_elt: (:class:`lxml.etree.Element` instance)
            Description element parent.
        :param indent: (integer, default=0)
            Indent value.
        :param width: (integer, default=60)
            Text width.
        :return: string
        """
        text = ' '.join(local_text(root_elt, 'description', lang=lang).split())
        if not indent and ' --' in text:
            return '\n'.join([fill(k.strip(), width, subsequent_indent='    ')
                              for k in text.split(' --')])

        subsequent_indent = '  |' + ' ' * (indent - 3)
        return fill(text, width, initial_indent=' ' * indent,
                    subsequent_indent=subsequent_indent).strip()

    # -------------------------------------------------------------------------
    @classmethod
    def _translate(cls, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(getdefaultlocale()[0]).translate(text)


# =============================================================================
if __name__ == '__main__':
    main()
