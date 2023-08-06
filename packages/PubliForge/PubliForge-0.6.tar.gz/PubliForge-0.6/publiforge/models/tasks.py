# $Id: tasks.py 216d9ea41de1 2012/05/19 09:15:54 patrick $
"""SQLAlchemy-powered model definition for project tasks."""

from lxml import etree
from textwrap import fill
from datetime import datetime
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import normalize_spaces
from . import LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession


XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Task(Base):
    """SQLAlchemy-powered project task model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    deadline = Column(types.Date)
    user_id = Column(types.Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'))
    processings = relationship('TaskProcessing')
    nexts = relationship('TaskNext')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, deadline=None):
        """Constructor method."""
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        if deadline is not None:
            self.deadline = (isinstance(deadline, basestring)
                and datetime.strptime(deadline, '%Y-%m-%d')) or deadline

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, task_elt):
        """Load a task from a XML file.

        :param project_id: (integer)
            Project ID.
        :param task_elt: (:class:`lxml.etree.Element` instance)
            Task XML element.
        :return: (integer)
            Task ID.
        """
        task = cls(project_id, task_elt.findtext('label'),
                   task_elt.findtext('description'),
                   task_elt.findtext('deadline'))
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
            for processing in sorted(self.processings,
                    key=lambda k: '%s%d' % (k.trigger, k.processing_id)):
                elt.append(processing.xml())
        if self.nexts:
            elt = etree.SubElement(task_elt, 'connections')
            for task_next in sorted(self.nexts, key=lambda k: k.next_id):
                elt.append(task_next.xml())

        return task_elt


# =============================================================================
class TaskProcessing(Base):
    """SQLAlchemy-powered project processing task model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'tasks_processings'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'task_id'],
            ['tasks.project_id', 'tasks.task_id'],
            ondelete='CASCADE'),
        ForeignKeyConstraint(['project_id', 'processing_id'],
            ['processings.project_id', 'processings.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    trigger = Column(
        types.Enum('in', 'manual', 'out', name='prjtskprc_step_enum'),
        primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, task_id, trigger, processing_id):
        """Constructor method."""
        self.project_id = project_id
        self.task_id = task_id
        self.trigger = trigger
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

        for child in task_elt.xpath('processings/processing'):
            processing_id = processings.get(child.get('ref'))
            if processing_id is not None:
                DBSession.add(cls(
                    project_id, task_id, child.get('trigger'), processing_id))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a task processing to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        processing_elt = etree.Element('processing')
        processing_elt.set(
            'ref', 'prc%d.%d' % (self.project_id, self.processing_id))
        processing_elt.set('trigger', self.trigger)
        return processing_elt


# =============================================================================
class TaskNext(Base):
    """SQLAlchemy-powered project next task model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'tasks_next'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'task_id'],
            ['tasks.project_id', 'tasks.task_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    task_id = Column(types.Integer, primary_key=True)
    next_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, task_id, next_id):
        """Constructor method."""
        self.project_id = project_id
        self.task_id = task_id
        self.next_id = next_id

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
        if task_elt.find('connections') is None:
            return
        task_id = tasks[task_elt.get('%sid' % XML_NS)]

        for child in task_elt.findall('connections/next'):
            next_id = tasks.get(child.get('task'))
            if next_id is not None:
                DBSession.add(cls(project_id, task_id, next_id))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a next task to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        next_elt = etree.Element('next')
        next_elt.set('task', 'tsk%d.%d' % (self.project_id, self.next_id))
        return next_elt
