# $Id: packs.py 77a5c869abcc 2012/09/02 18:01:52 patrick $
"""SQLAlchemy-powered model definition for project tasks."""

from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from lxml import etree
from textwrap import fill
from datetime import datetime

from ..lib.utils import normalize_spaces, export_file_set
from . import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from . import Base, DBSession
from .users import User
from .tasks import OPERATOR_TYPES


# =============================================================================
class Pack(Base):
    """SQLAlchemy-powered project pack model."""
    # pylint: disable = I0011, R0902, W0142

    __tablename__ = 'packs'
    __table_args__ = (
        UniqueConstraint('project_id', 'label'),
        ForeignKeyConstraint(
            ['project_id', 'task_id'],
            ['tasks.project_id', 'tasks.task_id']),
        {'mysql_engine': 'InnogDB'})

    project_id = Column(
        types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    recursive = Column(types.Boolean, default=False)
    note = Column(types.Text)
    task_id = Column(types.Integer)
    operator_type = Column(
        types.Enum(*OPERATOR_TYPES, name='operatortype_enum'))
    operator_id = Column(types.Integer, index=True)
    updated = Column(types.DateTime, onupdate=datetime.now)
    created = Column(types.DateTime, default=datetime.now)
    files = relationship('PackFile')
    events = relationship('PackEvent')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, recursive=False,
                 note=None, task_id=None, operator_type=None,
                 operator_id=None):
        """Constructor method."""
        # pylint: disable = I0011, R0913
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.recursive = bool(recursive)
        self.note = note and note.strip() or None
        if task_id and operator_type \
                and (operator_type == 'auto' or operator_id is not None):
            self.task_id = task_id
            self.operator_type = operator_type
            self.operator_id = operator_type != 'auto' and operator_id or None
        self.updated = datetime.now()
        self.created = self.updated

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, roles, tasks, pack_elt):
        """Load a pack from a XML file.

        :param project_id: (integer)
            Project ID.
        :param roles: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        :param tasks: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param pack_elt: (:class:`lxml.etree.Element` instance)
            Pack XML element.
        """
        # User cache
        users = {}

        def _update_users(login):
            """Update user dictionary."""
            if login and login not in users:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    users[login] = user.user_id

        def _operator_id(operator_type, operator_id):
            """Return database ID."""
            if operator_type == 'user':
                _update_users(operator_id)
                operator_id = users.get(operator_id)
            elif operator_type == 'role':
                operator_id = roles.get(operator_id)
            return operator_id

        # Read current task i.e. last event
        task_id = operator_type = operator_id = None
        child = pack_elt.find('events/event')
        if child is not None:
            ref = child.get('ref').split() or (None, None, None)
            task_id, operator_type = ref[0:2]
            task_id = tasks.get(task_id)
            operator_id = _operator_id(
                operator_type, len(ref) == 3 and ref[2] or None)

        # Create pack with its history
        pack = cls(
            project_id, pack_elt.findtext('label'),
            pack_elt.findtext('description'), pack_elt.get('recursive'),
            pack_elt.findtext('note'), task_id, operator_type, operator_id)
        for child in pack_elt.iterdescendants(tag=etree.Element):
            if child.tag in ('file', 'resource', 'template'):
                pack.files.append(PackFile(
                    child.tag, child.text.strip(), child.get('to'),
                    child.get('visible')))
            elif child.tag == 'event':
                ref = child.get('ref').split() or (None, None, None)
                task_id, operator_type = ref[0:2]
                operator_id = _operator_id(
                    operator_type, len(ref) == 3 and ref[2] or None)
                pack.events.append(PackEvent(
                    project_id, None, tasks.get(task_id), child.get('task'),
                    operator_type, operator_id, child.get('operator'),
                    child.get('begin')))

        DBSession.add(pack)
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a pack to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        # User cache
        users = {}

        def _update_users(user_id):
            """Update user dictionary."""
            if user_id not in users:
                user = DBSession.query(User).filter_by(user_id=user_id).first()
                if user is not None:
                    users[user_id] = user.login

        # Create pack
        pack_elt = etree.Element('pack')
        if self.recursive:
            pack_elt.set('recursive', 'true')
        etree.SubElement(pack_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(pack_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        export_file_set(pack_elt, self, 'file')
        export_file_set(pack_elt, self, 'resource')
        export_file_set(pack_elt, self, 'template')
        if self.note:
            etree.SubElement(pack_elt, 'note').text = self.note

        # Events
        if self.events:
            elt = etree.SubElement(pack_elt, 'events')
            for event in sorted(
                    self.events, key=lambda k: k.begin, reverse=True):
                elt.append(event.xml())

        return pack_elt


# =============================================================================
class PackFile(Base):
    """SQLAlchemy-powered project pack file model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'packs_files'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['packs.project_id', 'packs.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    file_type = Column(
        types.Enum('file', 'resource', 'template', name='pckfil_type_enum'),
        primary_key=True)
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


# =============================================================================
class PackEvent(Base):
    """SQLAlchemy-powered project pack task event model."""
    # pylint: disable = I0011, R0902, W0142

    __tablename__ = 'packs_events'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['packs.project_id', 'packs.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    begin = Column(types.DateTime, primary_key=True, default=datetime.now)
    task_id = Column(types.Integer)
    task_label = Column(types.String(LABEL_LEN), nullable=False)
    operator_type = Column(
        types.Enum(*OPERATOR_TYPES, name='operatortype_enum'))
    operator_id = Column(types.Integer)
    operator_label = Column(types.String(LABEL_LEN + 15), nullable=False)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, pack_id, task_id, task_label,
                 operator_type, operator_id, operator_label, begin=None):
        """Constructor method."""
        # pylint: disable = I0011, R0913
        self.project_id = project_id
        self.pack_id = pack_id
        self.begin = (
            isinstance(begin, basestring)
            and datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S')) or begin
        self.task_id = task_id
        self.task_label = normalize_spaces(task_label, LABEL_LEN)
        self.operator_type = operator_type
        self.operator_id = operator_id
        self.operator_label = normalize_spaces(operator_label, LABEL_LEN + 15)

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize an event to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        event_elt = etree.Element(
            'event', begin=self.begin.isoformat(), task=self.task_label,
            operator=self.operator_label)

        if self.operator_type == 'user':
            user = DBSession.query(User.login).filter_by(
                user_id=self.operator_id).first()
            if user is not None:
                event_elt.set(
                    'ref', 'tsk%d.%d user %s' % (
                        self.project_id, self.task_id, user[0]))
        elif self.operator_type == 'role':
            event_elt.set(
                'ref', 'tsk%d.%d role rol%d.%d' % (
                    self.project_id, self.task_id, self.project_id,
                    self.operator_id))
        else:
            event_elt.set(
                'ref', 'tsk%d.%d auto' % (self.project_id, self.task_id))

        return event_elt
