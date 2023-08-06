# $Id: test_scripts_pfbuild.py df43b426606b 2012/03/09 15:58:44 yvon $
# pylint: disable = I0011, R0904
"""Tests of ``scripts.pfbuild`` classes and functions."""

import unittest
from os.path import join, dirname

from ..tests import TEST_INI

ROOT = dirname(TEST_INI)
BUILD2HTML_FILE = join(ROOT, 'Examples', 'Builds', 'publidoc2html.pfb.xml')
BUILD2EPUB_FILE = join(ROOT, 'Examples', 'Builds', 'publidoc2epub.pfb.xml')
BUILD_ID = 'Test'
XML_ID = 'torture_test'


# =============================================================================
class DummyOption(object):
    """Class to simulate ``OptionParser`` option."""
    # pylint: disable = I0011, R0903

    build_id = BUILD_ID

    # -------------------------------------------------------------------------
    def __init__(self):
        """Constructor method."""
        self.list_processors = False
        self.list_variables = False
        self.show_variables = False
        self.processor_root = None
        self.storage_root = None
        self.build_root = None
        self.recursive = False


# =============================================================================
class BuildLauncherTestCase(unittest.TestCase):
    """Base unit test class for ``scripts.pfbuild.BuildLauncher``."""
    # pylint: disable = I0011, C0103

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(BuildLauncherTestCase, self).__init__(method_name)
        self._build_file = None
        self._build_tree = None
        self._storage_root = None
        self._build_root = None
        self._opts = DummyOption()

    # -------------------------------------------------------------------------
    def setUp(self):
        """Read configuration and clean up build directory."""

        # Read configuration file
        from os.path import normpath
        from ..lib.xml import load
        self._build_tree = load(self._build_file, {'publiforge':
            join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')})

        # Read storage path
        path = dirname(self._build_file)
        xpath = 'build/settings/setting[@key="%s"]'
        elt = self._build_tree.find(xpath % 'storage.root')
        if elt is not None:
            self._storage_root = normpath(join(path, elt.text.strip()))

        # Read build directory
        elt = self._build_tree.find(xpath % 'build.root')
        if elt is not None:
            self._build_root = normpath(join(path, elt.text.strip()))

        # Clean up build directory
        self.tearDown()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from os.path import exists
        from shutil import rmtree
        if self._build_root and exists(join(self._build_root, BUILD_ID)):
            rmtree(join(self._build_root, BUILD_ID))
        self._opts.storage_root = None
        self._opts.build_root = None

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``BuildLauncher`` object."""
        from ..scripts import pfbuild
        from ..lib.build import agent
        from logging import WARNING
        agent.LOG.setLevel(WARNING)
        pfbuild.LOG.setLevel(WARNING)
        return pfbuild.BuildLauncher(self._opts)


# =============================================================================
class UnitTestScriptsPFBuildBuildLauncherHTML(BuildLauncherTestCase):
    """Unit test class for ``scripts.pfbuild.BuildLauncher`` with HTML
    processing."""
    # pylint: disable = I0011, R0904, W0212

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(UnitTestScriptsPFBuildBuildLauncherHTML, self).\
            __init__(method_name)
        self._build_file = BUILD2HTML_FILE

    # -------------------------------------------------------------------------
    def test_read_settings(self):
        """[u:scripts.pfbuild.BuildLauncher._read_settings:HTML]"""
        launcher = self._make_one()
        settings = launcher._read_settings(self._build_file, self._build_tree)
        self.assertTrue('storage.root' in settings)
        self.assertEqual(settings['storage.root'], self._storage_root)
        self.assertTrue('build.root' in settings)
        self.assertEqual(settings['build.root'], self._build_root)

    # -------------------------------------------------------------------------
    def test_read_settings_with_options(self):
        """[u:scripts.pfbuild.BuildLauncher._read_settings:HTML] with option"""
        from os.path import expanduser
        self._opts.storage_root = '~/Storages'
        self._opts.build_root = '~/Builds'
        launcher = self._make_one()
        settings = launcher._read_settings(self._build_file, self._build_tree)
        self.assertTrue('storage.root' in settings)
        self.assertEqual(
            settings['storage.root'], expanduser(self._opts.storage_root))
        self.assertTrue('build.root' in settings)
        self.assertEqual(
            settings['build.root'], expanduser(self._opts.build_root))

    # -------------------------------------------------------------------------
    def test_read_processing(self):
        """[u:scripts.pfbuild.BuildLauncher._read_processing:HTML]"""
        from ..lib.build.agent import AgentBuildManager
        launcher = self._make_one()
        settings = {'storage.root': self._storage_root,
                    'build.root': self._build_root}
        build_manager = AgentBuildManager(settings)
        build_manager.processor_list()
        processing = launcher._read_processing(
            settings, build_manager, self._build_tree)
        self.assertTrue('processor_id' in processing)
        self.assertTrue('variables' in processing)
        self.assertTrue('resources' in processing)
        self.assertTrue('templates' in processing)

    # -------------------------------------------------------------------------
    def test_read_pack(self):
        """[u:scripts.pfbuild.BuildLauncher._read_pack:HTML]"""
        launcher = self._make_one()
        settings = {'storage.root': self._storage_root,
                    'build.root': self._build_root}
        pack = launcher._read_pack(settings, self._build_tree, [])
        self.assertTrue('recursive' in pack)
        self.assertTrue('files' in pack)
        self.assertTrue('resources' in pack)
        self.assertTrue('templates' in pack)

    # -------------------------------------------------------------------------
    def test_read_pack_with_files(self):
        """[u:scripts.pfbuild.BuildLauncher._read_pack:HTML] with file"""
        from os.path import relpath
        launcher = self._make_one()
        settings = {'storage.root': self._storage_root,
                    'build.root': self._build_root}
        pack = launcher._read_pack(
            settings, self._build_tree, [self._build_file])
        self.assertTrue('files' in pack)
        self.assertTrue(
            relpath(self._build_file, self._storage_root) in pack['files'])

    # -------------------------------------------------------------------------
    def test_start(self):
        """[u:script.pfbuild.BuildLauncher.start:HTML]"""
        from os.path import exists
        from ..lib.utils import camel_case
        launcher = self._make_one()
        launcher.start(self._build_file, {})
        path = join(self._build_root, BUILD_ID, 'Processor')
        self.assertTrue(exists(join(path, 'processor.xml')))
        self.assertTrue(exists(join(path, 'leprisme.ini')))
        self.assertTrue(exists(join(path, 'lib')))
        self.assertTrue(exists(join(path, 'Templates')))
        self.assertTrue(exists(join(path, 'Regex')))
        self.assertTrue(exists(join(path, 'RelaxNG')))
        self.assertTrue(exists(join(path, 'Xsl', 'publidoc2html.xsl')))
        path = join(self._build_root, BUILD_ID, 'Output', camel_case(XML_ID))
        self.assertTrue(exists(join(path, 'Css')))
        self.assertTrue(exists(join(path, 'Images')))
        self.assertTrue(exists(join(path, 'RelaxNG')))
        self.assertTrue(exists(join(path, '%s.html' % XML_ID)))
        self.assertTrue(exists(join(path, '%s-tpc-1.html' % XML_ID)))


# =============================================================================
class UnitTestScriptsPFBuildBuildLauncherEPub(BuildLauncherTestCase):
    """Unit test class for ``scripts.pfbuild.BuildLauncher`` with ePub
    processing."""

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(UnitTestScriptsPFBuildBuildLauncherEPub, self).\
            __init__(method_name)
        self._build_file = BUILD2EPUB_FILE

    # -------------------------------------------------------------------------
    def test_start(self):
        """[u:scripts.pfbuild.BuildLauncher.start:ePub]"""
        from os.path import exists
        from ..lib.utils import camel_case
        launcher = self._make_one()
        launcher.start(self._build_file, {})
        path = join(self._build_root, BUILD_ID, 'Processor')
        self.assertTrue(exists(join(path, 'processor.xml')))
        self.assertTrue(exists(join(path, 'leprisme.ini')))
        self.assertTrue(exists(join(path, 'Templates', 'Publidoc2EPub')))
        self.assertTrue(exists(join(path, 'Templates', 'Publidoc2Html')))
        self.assertTrue(exists(join(path, 'jars')))
        self.assertTrue(exists(join(path, 'Xsl', 'publidoc2html.xsl')))
        self.assertTrue(exists(join(path, 'Xsl', 'publidoc2epub.xsl')))
        path = join(self._build_root, BUILD_ID, 'Output', camel_case(XML_ID))
        self.assertTrue(exists(join(path, '%s.epub' % XML_ID)))
