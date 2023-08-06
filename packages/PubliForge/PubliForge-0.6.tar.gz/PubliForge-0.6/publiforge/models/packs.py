# $Id: packs.py 9a5ee924a2f3 2012/05/19 15:05:40 patrick $
"""SQLAlchemy-powered model definition for project tasks."""

from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from lxml import etree
from textwrap import fill

from ..lib.utils import normalize_spaces, export_file_set
from . import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from . import Base, DBSession


# =============================================================================
class Pack(Base):
    """SQLAlchemy-powered project pack model."""

    __tablename__ = 'packs'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    recursive = Column(types.Boolean, default=False)
    files = relationship('PackFile')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, recursive=False):
        """Constructor method."""
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.recursive = bool(recursive)

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, pack_elt):
        """Load a pack from a XML file.

        :param pack_elt: (:class:`lxml.etree.Element` instance)
            Pack XML element.
        """
        pack = cls(project_id, pack_elt.findtext('label'),
                   pack_elt.findtext('description'),
                   pack_elt.get('recursive'))
        for child in pack_elt.iterdescendants(tag=etree.Element):
            if child.tag in ('file', 'resource', 'template'):
                pack.files.append(PackFile(
                    child.tag, child.text.strip(), child.get('to'),
                    child.get('visible')))

        DBSession.add(pack)
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a pack to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        pack_elt = etree.Element('pack')
        if self.recursive:
            pack_elt.set('recursive', 'true')
        etree.SubElement(pack_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(pack_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        export_file_set(pack_elt, self, 'file', False)
        export_file_set(pack_elt, self, 'resource', False,)
        export_file_set(pack_elt, self, 'template', False)

        return pack_elt


# =============================================================================
class PackFile(Base):
    """SQLAlchemy-powered project pack file model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'packs_files'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'pack_id'],
            ['packs.project_id', 'packs.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    file_type = Column(types.Enum('file', 'resource', 'template',
        name='prjpckfil_type_enum'), primary_key=True)
    path = Column(types.String(PATH_LEN), primary_key=True)
    target = Column(types.String(PATH_LEN))
    visible = Column(types.Boolean())

    # -------------------------------------------------------------------------
    def __init__(self, file_type, path, target=None, visible=None):
        """Constructor method."""
        self.file_type = file_type
        self.path = path.strip()[0:PATH_LEN]
        self.target = (target and target.strip()[0:PATH_LEN]) \
            or (file_type == 'template'
                and self.path.partition('/')[2][0:PATH_LEN]) or None
        self.visible = (visible is None and file_type == 'file' and True) \
            or (visible if isinstance(visible, bool) else (visible == 'true'))
