# $Id: test_lib_xml.py 68b0cb3c67d5 2011/12/18 18:50:45 patrick $
# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``lib.xml`` classes and functions."""

import unittest
from os.path import join, dirname

XML_FILE = join(
    dirname(__file__), '..', 'Processors', 'PublidocValid', 'processor.xml')
INI_FILE = join(
    dirname(__file__), '..', 'Processors', 'Publidoc2Html', 'leprisme.ini')


# =============================================================================
class UnitTestLibUtilsLoad(unittest.TestCase):
    """Unit test class for ``lib.xml.load``."""

    # -------------------------------------------------------------------------
    @classmethod
    def _call_fut(cls, filename, relaxngs=None, data=None):
        """Call function under test."""
        from ..lib.xml import load
        if relaxngs is None:
            relaxngs = {'publiforge':
                join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}
        return load(filename, relaxngs, data)

    # -------------------------------------------------------------------------
    def test_not_well_formed(self):
        """[u:lib.xml.load] not well-formed XML"""
        tree = self._call_fut(INI_FILE)
        self.assertTrue(isinstance(tree, basestring))
        self.assertTrue('not well-formed' in tree)

    # -------------------------------------------------------------------------
    def test_invalid(self):
        """[u:lib.xml.load] invalid XML"""
        with open(XML_FILE, 'r') as hdl:
            data = hdl.read().replace('engine', 'motor')
        tree = self._call_fut(XML_FILE, data=data)
        self.assertTrue(isinstance(tree, basestring))
        self.assertTrue('RELAXNG_ERR_ELEMWRONG' in tree)

    # -------------------------------------------------------------------------
    def test_valid_xml(self):
        """[u:lib.xml.load] valid XML"""
        tree = self._call_fut(XML_FILE)
        self.assertFalse(isinstance(tree, basestring))
