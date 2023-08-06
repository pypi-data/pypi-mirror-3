# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``models.processors`` classes."""

from os.path import dirname, join
from ..tests import ModelTestCase


# =============================================================================
class UnitTestModelsProcessorssProcessor(ModelTestCase):
    """Unit test class for ``models.processor.Processor``."""
    # pylint: disable = I0011, C0103

    _processor_path = join(dirname(__file__), 'Data', 'processor.xml')
    _processor_id = u'TestProcessor'
    _processor_xml = ' '
    _settings = {'storage.root': '/', 'agent.refresh': 180, \
                 'agent.0.weight': 1, 'agent.0.password': 'yo', \
                 'uid': 'devfront', 'pyramid.default_locale_name': 'en'}

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.processors import Processor
        self.session.query(Processor)\
            .filter_by(processor_id=self._processor_id).delete()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``Processor`` object."""
        from ..models.processors import Processor
        processor = Processor(self._processor_id)
        return processor

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.processors.Processor.__init__]"""
        from ..models.processors import Processor
        processor1 = self._make_one()
        with open(self._processor_path, 'r') as f:
            self._processor_xml = f.read()
        Processor.load(processor1.processor_id, self._processor_xml)
        self.session.add(processor1)
        self.session.commit()
        processor2 = self.session.query(Processor)\
                     .filter_by(processor_id=processor1.processor_id).first()
        self.assertNotEqual(processor2, None)
        self.assertEqual(processor2.processor_id, processor1.processor_id)
        self.assertEqual(processor2.xml, processor1.xml)
        self.assertEqual(processor2.description, processor1.description)

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.processors.Processor.__repr__]"""
        processor = self._make_one()
        info = repr(processor)
        self.assertTrue('<Processor(' in info)
        self.assertTrue('%s' % self._processor_id in info)

    # -------------------------------------------------------------------------
    def test_labels(self):
        """[u:models.processors.Processor.labels]"""
        from ..models.processors import Processor

        processor1 = self._make_one()
        self.session.add(processor1)
        self.session.commit()
        with open(self._processor_path, 'r') as f:
            self._processor_xml = f.read()
        Processor.load(processor1.processor_id, self._processor_xml)
        processor2 = self.session.query(Processor)\
                     .filter_by(processor_id=processor1.processor_id).first()
        request = self._make_request()
        request.registry.settings = self._settings
        request.registry['fbuild'] = FrontBuildManager()
        labels_dic = Processor.labels(request)
        self.assertTrue(labels_dic[processor2.processor_id] is not None)
        self.assertEqual(processor2.processor_id, processor1.processor_id)

    # -------------------------------------------------------------------------
    def test_description(self):
        """[u:models.processors.Processor.description]"""
        from ..models.processors import Processor
        from lxml import etree
        from ..lib.xml import local_text
        from cStringIO import StringIO

        processor1 = self._make_one()
        self.session.add(processor1)
        self.session.commit()
        with open(self._processor_path, 'r') as f:
            self._processor_xml = f.read()
        Processor.load(processor1.processor_id, self._processor_xml)
        processor2 = self.session.query(Processor)\
                     .filter_by(processor_id=processor1.processor_id).first()
        request = self._make_request()
        request.session['lang'] = 'en'
        request.registry.settings = self._settings
        request.registry['fbuild'] = FrontBuildManager()
        description2 = Processor.description(request, processor2.processor_id)

        xml = etree.parse(StringIO(self._processor_xml))
        description1 = local_text(xml.find('processor'), \
                                  'description', request)
        self.assertTrue(description2 is not None)
        self.assertEqual(description1, description2)


# =============================================================================
class FrontBuildManager(object):
    """This class manages front builds.

    Fake FrontBuildManager for Testing.
    """
    # pylint: disable = I0011, R0902

    # -------------------------------------------------------------------------
    def __init__(self):
        """Constructor method.
        """

    # -------------------------------------------------------------------------
    @classmethod
    def refresh_agent_list(cls, request):
        """empty function to bypass agents network request.
        """
        # pylint: disable = I0011, W0613
        return
