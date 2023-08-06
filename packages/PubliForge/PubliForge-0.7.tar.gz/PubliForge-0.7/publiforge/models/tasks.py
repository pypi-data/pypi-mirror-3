# $Id: tasks.py a37c7448c674 2012/09/04 17:19:30 patrick $
"""SQLAlchemy-powered model definition for project tasks."""

from lxml import etree
from textwrap import fill
from datetime import datetime
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_spaces
from . import LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession
from .users import User


OPERATOR_TYPES = ('user', 'role', 'auto')
LINK_TYPES = {'normal': _('normal'), 'back': _('back')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Task(Base):
    """SQLAlchemy-powered task model."""
    # pylint: disable = I0011, W0142

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer, ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    deadline = Column(types.Date)
    operator_type = Column(
        types.Enum(*OPERATOR_TYPES, name='operatortype_enum'),
        nullable=False)
    operator_id = Column(types.Integer)
    processings = relationship('TaskProcessing')
    links = relationship('TaskLink')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, deadline=None,
                 operator_type='user', operator_id=None):
        """Constructor method."""
        # pylint: disable = I0011, R0913
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = \
            normalize_spaces(description, DESCRIPTION_LEN) or None
        if deadline is not None:
            self.deadline = (
                isinstance(deadline, basestring)
                and datetime.strptime(deadline, '%Y-%m-%d')) or deadline
        self.operator_type = operator_type
        self.operator_id = operator_id

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, roles, task_elt):
        """Load a task from a XML file.

        :param project_id: (integer)
            Project ID.
        :param task_elt: (:class:`lxml.etree.Element` instance)
            Task XML element.
        :param roles: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        :return: (:class:`pyramid.i18n.TranslationString` or integer)
            Error message ort ask ID.
        """
        # Find operator
        operator = task_elt.find('operator')
        operator_id = operator.get('id')
        if operator.get('type') == 'user':
            user = DBSession.query(User).filter_by(login=operator_id).first()
            if user is None:
                return _(
                    '${t}: Incorrect task definition',
                    {'t': task_elt.get('%sid' % XML_NS)})
            operator_id = user.user_id
        elif operator.get('type') == 'role':
            if operator_id not in roles:
                return _(
                    '${t}: Incorrect task definition',
                    {'t': task_elt.get('%sid' % XML_NS)})
            operator_id = roles[operator_id]

        # Create task
        task = cls(
            project_id, task_elt.findtext('label'),
            task_elt.findtext('description'), task_elt.findtext('deadline'),
            operator.get('type'), operator_id)
        DBSession.add(task)
        DBSession.commit()

        return task.task_id

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a task to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        task_elt = etree.Element('task')
        task_elt.set(
            '%sid' % XML_NS, 'tsk%d.%d' % (self.project_id, self.task_id))
        etree.SubElement(task_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(task_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        if self.processings:
            elt = etree.SubElement(task_elt, 'processings')
            for processing in self.processings:
                elt.append(processing.xml())
        elt = etree.SubElement(task_elt, 'operator', type=self.operator_type)
        if self.operator_type == 'user':
            elt.set(
                'id', DBSession.query(User).filter_by(
                    user_id=self.operator_id).first().login)
        elif self.operator_type == 'role':
            elt.set('id', 'rol%s.%d' % (self.project_id, self.operator_id))
        if self.links:
            elt = etree.SubElement(task_elt, 'links')
            for task_link in sorted(self.links, key=lambda k: k.target_id):
                elt.append(task_link.xml())

        return task_elt


# =============================================================================
class TaskProcessing(Base):
    """SQLAlchemy-powered processing task model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'tasks_processings'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processings.project_id', 'processings.processing_id'],
            ondelete='CASCADE'),
        ForeignKeyConstraint(
            ['project_id', 'task_id'],
            ['tasks.project_id', 'tasks.task_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, task_id, processing_id):
        """Constructor method."""
        self.project_id = project_id
        self.task_id = task_id
        self.processing_id = processing_id

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, tasks, processings, task_elt):
        """Load a task processing from a XML file.

        :param project_id: (integer)
            Project ID.
        :param tasks: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param processings: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        :param task_elt: (:class:`lxml.etree.Element` instance)
            Task XML element.
        """
        if task_elt.find('processings') is None:
            return
        task_id = tasks[task_elt.get('%sid' % XML_NS)]

        for child in task_elt.findall('processings/processing'):
            processing_id = processings.get(child.get('ref'))
            if processing_id is not None:
                DBSession.add(cls(project_id, task_id, processing_id))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a task processing to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        processing_elt = etree.Element(
            'processing',
            ref='prc%d.%d' % (self.project_id, self.processing_id))
        return processing_elt


# =============================================================================
class TaskLink(Base):
    """SQLAlchemy-powered link task model."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'tasks_links'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'task_id'],
            ['tasks.project_id', 'tasks.task_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    target_id = Column(types.Integer, primary_key=True)
    link_type = Column(
        types.Enum(*LINK_TYPES.keys(), name='tasklinktype_enum'),
        default='normal')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, task_id, target_id, link_type=None):
        """Constructor method."""
        self.project_id = project_id
        self.task_id = task_id
        self.target_id = target_id
        self.link_type = link_type

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, tasks, task_elt):
        """Load a next task from a XML file.

        :param project_id: (integer)
            Project ID.
        :param tasks: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param task_elt: (:class:`lxml.etree.Element` instance)
            Task XML element.
        """
        if task_elt.find('links') is None:
            return
        task_id = tasks[task_elt.get('%sid' % XML_NS)]

        for child in task_elt.findall('links/link'):
            target_id = tasks.get(child.get('task'))
            if target_id is not None:
                DBSession.add(cls(
                    project_id, task_id, target_id, child.get('type')))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a next task to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        link_elt = etree.Element(
            'link', task='tsk%d.%d' % (self.project_id, self.target_id))
        if self.link_type != 'next':
            link_elt.set('type', self.link_type)
        return link_elt
