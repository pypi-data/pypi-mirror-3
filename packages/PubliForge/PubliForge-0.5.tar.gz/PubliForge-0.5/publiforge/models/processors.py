# $Id: processors.py 686a5b4faf1e 2012/01/05 22:44:46 patrick $
"""SQLAlchemy-powered model definition for processors."""

from time import time
from os.path import join, dirname
from cStringIO import StringIO
from lxml import etree

from sqlalchemy import Column, types

from ..lib.xml import local_text, load
from . import Base, DBSession, ID_LEN


# =============================================================================
class Processor(Base):
    """SQLAlchemy-powered processor model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'processors'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    processor_id = Column(types.String(ID_LEN), primary_key=True)
    xml = Column(types.Text())
    updated = Column(types.Float())

    # -------------------------------------------------------------------------
    def __init__(self, processor_id):
        """Constructor method."""
        self.processor_id = processor_id.strip()[0:ID_LEN]
        self.updated = time()

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<Processor('{processor_id}')>".format(
            processor_id=self.processor_id)

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, processor_id, xml):
        """Load a processor from a XML string.

        :param processor_id: (string)
            Processor ID.
        :param xml: (string)
            XML string.
        :return: (string, :class:`pyramid.i18n.TranslationString` or
            :class:`Processor`)
            Error message or processor object.
        """
        if isinstance(xml, unicode):
            xml = xml.encode('utf8')
        tree = load('processor.xml', {'publiforge':
            join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}, xml)
        if isinstance(tree, basestring):
            return tree

        # Check if already exists
        processor = DBSession.query(cls).filter_by(
            processor_id=processor_id).first()
        if processor is None:
            processor = cls(processor_id)

        processor.xml = xml.decode('utf8')
        processor.updated = time()

        return processor

    # -------------------------------------------------------------------------
    @classmethod
    def labels(cls, request):
        """Labels of all processors in local language or default language.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (dictionary)
            A dictionary such as ``{<processor_id>:
            <processor_label>,...}``.

        If some labels do not exist in the asked language, this method returns
        the label in default language or ``processor_id``.
        """
        request.registry['fbuild'].refresh_agent_list(request)
        labels = {}
        for processor in DBSession.query(cls.processor_id, cls.xml):
            tree = etree.parse(StringIO(processor[1].encode('utf8')))
            labels[processor[0]] = local_text(
                tree.find('processor'), 'label', request, default=processor[0])

        return labels

    # -------------------------------------------------------------------------
    @classmethod
    def description(cls, request, processor_id=None, xml=None):
        """Description of processor ``processor_id`` in local language or
        default language.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processor_id: (string, optional)
            Processor ID.
        :param xml: (:class:`lxml.etree.ElementTree` instance, optional)
            Processor XML.
        :return: (string)
            Description.

        If some labels do not exist in the asked language, this method returns
        the label in default language or ``processor_id``.
        """
        if processor_id is not None:
            request.registry['fbuild'].refresh_agent_list(request)
            xml = DBSession.query(cls.xml).filter_by(
                processor_id=processor_id).first()
            if xml is not None:
                xml = etree.parse(StringIO(xml[0].encode('utf8')))
        if xml:
            return local_text(xml.find('processor'), 'description', request)
