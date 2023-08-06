# $Id: projects.py 216d9ea41de1 2012/05/19 09:15:54 patrick $
"""SQLAlchemy-powered model definition for projects."""

from lxml import etree
from textwrap import fill
from datetime import datetime
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_name, normalize_spaces
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession
from .users import User
from .groups import Group
from .processings import Processing
from .packs import Pack
from .tasks import Task, TaskNext, TaskProcessing


PROJECT_STATUS = {'draft': _('Draft'), 'active': _('Active'),
                  'archived': _('Archived')}
PROJECT_PERMS = {'editor': _('Leader'), 'user': _('User')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Project(Base):
    """SQLAlchemy-powered project model."""
    # pylint: disable = I0011, W0142

    __tablename__ = 'projects'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    status = Column(types.Enum(*PROJECT_STATUS.keys(), name='prj_status_enum'),
                    nullable=False, default='active')
    deadline = Column(types.Date)
    users = relationship('ProjectUser', backref='project')
    groups = relationship('ProjectGroup')
    processings = relationship('Processing')
    packs = relationship('Pack')
    tasks = relationship('Task')

    # -------------------------------------------------------------------------
    def __init__(self, label, description=None, status=None, deadline=None):
        """Constructor method."""
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.status = status
        if deadline is not None:
            self.deadline = (isinstance(deadline, basestring)
                and datetime.strptime(deadline, '%Y-%m-%d')) or deadline

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_elt, error_if_exists=True):
        """Load a project from a XML file.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if project already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        label = normalize_spaces(project_elt.findtext('label'), LABEL_LEN)
        project = DBSession.query(cls).filter_by(label=label).first()
        if project is not None:
            if error_if_exists:
                return _('Project "${l}" already exists.', {'l': label})
            return

        # Create project
        project = cls(project_elt.findtext('label'),
                      project_elt.findtext('description'),
                      project_elt.get('status', 'active'),
                      project_elt.findtext('deadline'))
        DBSession.add(project)
        DBSession.commit()

        # Append processings
        processings = {}
        elt = project_elt.find('processings')
        if elt is not None:
            for child in elt.iterchildren(tag=etree.Element):
                processings[child.get('%sid' % XML_NS)] = \
                    Processing.load(project.project_id, child, False)
            Processing.correct_processing_variables(
                project.project_id, processings)

        # Append packs
        elt = project_elt.find('packs')
        if elt is not None:
            for child in elt.iterchildren(tag=etree.Element):
                Pack.load(project.project_id, child)

        # Append tasks
        elt = project_elt.find('tasks')
        if elt is not None:
            tasks = {}
            for child in elt.iterchildren(tag=etree.Element):
                tasks[child.get('%sid' % XML_NS)] = \
                    Task.load(project.project_id, child)
            for child in elt.iterchildren(tag=etree.Element):
                TaskNext.load(project.project_id, tasks, child)
                TaskProcessing.load(
                    project.project_id, tasks, processings, child)

        # Append team
        cls._load_team(project_elt, project)

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, request):
        """Serialize a project to a XML representation.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (:class:`lxml.etree.Element`)
        """
        # Header
        project_elt = etree.Element('project')
        project_elt.set('status', self.status)
        etree.SubElement(project_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(project_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 8,
                subsequent_indent=' ' * 8)
        if self.deadline:
            etree.SubElement(project_elt, 'deadline')\
                .text = self.deadline.isoformat()

        # Processings
        if self.processings:
            group_elt = etree.SubElement(project_elt, 'processings')
            for processing \
                    in sorted(self.processings, key=lambda k: k.processing_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Processing: %s ' % processing.label)))
                processor = request.registry['fbuild'].processor(
                    request, processing.processor)
                group_elt.append(processing.xml(processor))

        # Packs
        if self.packs:
            group_elt = etree.SubElement(project_elt, 'packs')
            for pack in sorted(self.packs, key=lambda k: k.pack_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Pack: %s ' % pack.label)))
                group_elt.append(pack.xml())

        # Tasks
        if self.tasks:
            group_elt = etree.SubElement(project_elt, 'tasks')
            for task in sorted(self.tasks, key=lambda k: k.task_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Task: %s ' % task.label)))
                group_elt.append(task.xml())

        # Team
        self._xml_team(project_elt)

        return project_elt

    # -------------------------------------------------------------------------
    @classmethod
    def _load_team(cls, project_elt, project):
        """Load users and groups for project.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
        :param project: (:class:`Project` instance)
            SQLAlchemy-powered Project object.
        """
        # Users
        done = []
        for item in project_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if not login in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    project.users.append(ProjectUser(
                        project.project_id, user.user_id, item.get('in-menu'),
                        item.get('permission', 'user')))
                done.append(login)

        # Groups
        done = []
        for item in project_elt.findall('members/member-group'):
            group_id = normalize_name(item.text)[0:ID_LEN]
            if group_id not in done:
                done.append(group_id)
                group = DBSession.query(Group).filter_by(
                    group_id=group_id).first()
                if group is not None:
                    project.groups.append(ProjectGroup(project.project_id,
                        group.group_id, item.get('permission', 'user')))

    # -------------------------------------------------------------------------
    def _xml_team(self, project_elt):
        """Serialize users and groups to a XML representation.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
        """
        if not self.users and not self.groups:
            return
        project_elt.append(etree.Comment(u'{0:~^66}'.format(' Team ')))

        # Users
        group_elt = etree.SubElement(project_elt, 'members')
        for user in self.users:
            elt = etree.SubElement(group_elt, 'member')
            elt.text = user.user.login
            if user.perm != 'user':
                elt.set('permission', user.perm or 'none')
            if user.in_menu:
                elt.set('in-menu', 'true')

        # Groups
        for group in self.groups:
            elt = etree.SubElement(group_elt, 'member-group')
            elt.text = group.group_id
            if group.perm != 'user':
                elt.set('permission', group.perm)


# =============================================================================
class ProjectUser(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``User``."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'projects_users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    user_id = Column(types.Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True)
    in_menu = Column(types.Boolean(), default=False)
    perm = Column(types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'))
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, user_id, in_menu=False, perm=None):
        """Constructor method."""
        self.project_id = project_id
        self.user_id = user_id
        self.in_menu = bool(in_menu)
        if perm != 'none':
            self.perm = perm


# =============================================================================
class ProjectGroup(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``Group``."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'projects_groups'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    group_id = Column(types.String(ID_LEN),
        ForeignKey('groups.group_id', ondelete='CASCADE'),
        primary_key=True)
    perm = Column(types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'),
                  default='user')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, group_id, perm=None):
        """Constructor method."""
        self.project_id = project_id
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm
