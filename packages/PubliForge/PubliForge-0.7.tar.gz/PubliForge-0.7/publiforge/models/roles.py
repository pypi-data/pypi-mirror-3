# $Id: roles.py c0062fcc9f82 2012/07/22 19:34:51 patrick $
"""SQLAlchemy-powered model definition for roles."""

from lxml import etree
from textwrap import fill
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import normalize_spaces
from . import Base, DBSession, LABEL_LEN, DESCRIPTION_LEN


XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Role(Base):
    """SQLAlchemy-powered role model."""

    __tablename__ = 'roles'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    role_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    users = relationship('RoleUser')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None):
        """Constructor method."""
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = \
            normalize_spaces(description, DESCRIPTION_LEN) or None

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, role_elt):
        """Load a user from a XML file.

        :param project_id: (integer)
            Project ID.
        :param role_elt: (:class:`lxml.etree.Element` instance)
            Role XML element.
        :return: (integer)
            Role ID.
        """
        role = cls(project_id, role_elt.findtext('label'),
                   role_elt.findtext('description'))
        DBSession.add(role)
        DBSession.commit()

        return role.role_id

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a role to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        role_elt = etree.Element('role')
        role_elt.set(
            '%sid' % XML_NS, 'rol%d.%d' % (self.project_id, self.role_id))
        etree.SubElement(role_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(role_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)

        return role_elt


# =============================================================================
class RoleUser(Base):
    """SQLAlchemy-powered association table between ``Role`` and
    ``User``."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'roles_users'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'role_id'],
            ['roles.project_id', 'roles.role_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    role_id = Column(types.Integer, primary_key=True)
    user_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, role_id, user_id):
        """Constructor method."""
        self.project_id = project_id
        self.role_id = role_id
        self.user_id = user_id
