# $Id: test_lib_utils.py 68b0cb3c67d5 2011/12/18 18:50:45 patrick $
# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``lib.utils`` classes and functions."""

import unittest
from os.path import join, dirname

INI_FILE = join(
    dirname(__file__), '..', 'Processors', 'Publidoc2Html', 'leprisme.ini')
CONTENT_DIR = join(dirname(__file__), '..', 'Processors', 'PublidocValid')
CONTENT_EXCLUDE = ('.hg', 'publiset.rng')


# =============================================================================
class UnitTestLibUtilsConfigGet(unittest.TestCase):
    """Unit test class for ``lib.utils.config_get``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.config_get]"""
        from ConfigParser import ConfigParser
        from ..lib.utils import config_get
        config = ConfigParser({'here': dirname(INI_FILE)})
        config.read(INI_FILE)
        self.assertEqual(config_get(config, 'Input', 'file_regex'), r'\.xml$')
        self.assertEqual(config_get(config, 'Input', 'foo', 'bar'), 'bar')


# =============================================================================
class UnitTestLibUtilsCopyContent(unittest.TestCase):
    """Unit test class for ``lib.utils.copy_content``."""
    # pylint: disable = I0011, C0103

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(UnitTestLibUtilsCopyContent, self).__init__(method_name)
        self._tmp_dir = None

    # -------------------------------------------------------------------------
    def setUp(self):
        """Create a temporary directory."""
        from tempfile import mkdtemp
        self.tearDown()
        self._tmp_dir = mkdtemp()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from os.path import exists
        from shutil import rmtree
        if self._tmp_dir is not None and exists(self._tmp_dir):
            rmtree(self._tmp_dir)
        self._tmp_dir = None

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.copy_content]"""
        from os import walk
        from os.path import exists, relpath
        from ..lib.utils import copy_content
        copy_content(CONTENT_DIR, self._tmp_dir, CONTENT_EXCLUDE)
        for path, dirs, files in walk(CONTENT_DIR):
            for name in dirs + files:
                copy = join(self._tmp_dir, relpath(path, CONTENT_DIR), name)
                if name in CONTENT_EXCLUDE:
                    self.assertFalse(exists(copy))
                else:
                    self.assertTrue(exists(copy))


# =============================================================================
class UnitTestLibUtilsCamelCase(unittest.TestCase):
    """Unit test class for ``lib.utils.camel_case``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.camel_case]"""
        from ..lib.utils import camel_case
        self.assertEqual(camel_case('pdoc2html'), 'Pdoc2Html')
        self.assertEqual(camel_case('LaTeX'), 'LaTeX')
        self.assertEqual(camel_case('laTeX'), 'LaTeX')
        self.assertEqual(camel_case('my_way'), 'MyWay')
        self.assertEqual(camel_case('my way'), 'MyWay')
        self.assertEqual(camel_case('my-way'), 'My-Way')


# =============================================================================
class UnitTestLibUtilsHashSha(unittest.TestCase):
    """Unit test class for ``lib.utils.hash_sha``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.hash_sha]"""
        from ..lib.utils import hash_sha
        self.assertEqual(hash_sha('protectme', None),
                         '360a06e80743072020f69f2129c4933ea29f879f')
        self.assertEqual(hash_sha('protectme', 'seekrit'),
                         'e50267004c95597d525f9a16e68d046c80eb0ded')
        self.assertEqual(hash_sha(u'protègemoi', None),
                         'c4eb986ca838b6e2dc6c4b1bdfa31142ea565a84')


# =============================================================================
class UnitTestLibUtilsEncrypt(unittest.TestCase):
    """Unit test class for ``lib.utils.encrypt``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.encrypt]"""
        from ..lib.utils import encrypt
        self.assertEqual(encrypt('protectme', None),
                         'XzgU2PN974c3yYOp4FsJzw==')
        self.assertEqual(encrypt('protectme', 'seekrit'),
                         'B/48LdYirNqHOFq3dMIWQA==')
        self.assertEqual(encrypt('protègemoi', 'seekrit'),
                         'GoJ3XiMjxaXqm6eDr9anfg==')


# =============================================================================
class UnitTestLibUtilsDecrypt(unittest.TestCase):
    """Unit test class for ``lib.utils.decrypt``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.decrypt]"""
        from ..lib.utils import decrypt
        self.assertEqual(decrypt('XzgU2PN974c3yYOp4FsJzw==', None),
                         'protectme')
        self.assertEqual(decrypt('B/48LdYirNqHOFq3dMIWQA==', 'seekrit'),
                         'protectme')
        self.assertEqual(decrypt('GoJ3XiMjxaXqm6eDr9anfg==', 'seekrit'),
                         'protègemoi')
