# $Id: projects.py f8e74dc99563 2012/07/30 14:15:15 patrick $
"""SQLAlchemy-powered model definition for projects."""

from lxml import etree
from textwrap import fill
from datetime import datetime
from sqlalchemy import or_, and_, Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_name, normalize_spaces
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession
from .roles import Role, RoleUser
from .processings import Processing
from .packs import Pack
from .tasks import Task, TaskLink, TaskProcessing
from .users import User
from .groups import GROUPS_USERS, Group


PROJECT_STATUS = {'draft': _('Draft'), 'active': _('Active'),
                  'archived': _('Archived')}
PROJECT_PERMS = {'leader': _('Leader'), 'user': _('User')}
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
    roles = relationship('Role')
    processings = relationship('Processing')
    packs = relationship('Pack')
    tasks = relationship('Task')
    users = relationship('ProjectUser', backref='project')
    groups = relationship('ProjectGroup')

    # -------------------------------------------------------------------------
    def __init__(self, label, description=None, status=None, deadline=None):
        """Constructor method."""
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.status = status
        if deadline is not None:
            self.deadline = (
                isinstance(deadline, basestring)
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

        # Append roles
        roles = {}
        elt = project_elt.find('roles')
        if elt is not None:
            for child in elt.findall('role'):
                roles[child.get('%sid' % XML_NS)] = \
                    Role.load(project.project_id, child)

        # Append team
        cls._load_team(project, roles, project_elt)

        # Append processings
        processings = {}
        elt = project_elt.find('processings')
        if elt is not None:
            for child in elt.findall('processing'):
                processings[child.get('%sid' % XML_NS)] = \
                    Processing.load(project.project_id, child, False)
            Processing.correct_processing_variables(
                project.project_id, processings)

        # Append tasks
        tasks = {}
        elt = project_elt.find('tasks')
        if elt is not None:
            for child in elt.findall('task'):
                tasks[child.get('%sid' % XML_NS)] = \
                    Task.load(project.project_id, roles, child)
                if not isinstance(tasks[child.get('%sid' % XML_NS)], int):
                    return tasks[child.get('%sid' % XML_NS)]
            for child in elt.findall('task'):
                TaskLink.load(project.project_id, tasks, child)
                TaskProcessing.load(
                    project.project_id, tasks, processings, child)

        # Append packs
        elt = project_elt.find('packs')
        if elt is not None:
            for child in elt.findall('pack'):
                Pack.load(project.project_id, roles, tasks, child)

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

        # Roles
        if self.roles:
            group_elt = etree.SubElement(project_elt, 'roles')
            for role in sorted(self.roles, key=lambda k: k.role_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Role: %s ' % role.label)))
                group_elt.append(role.xml())

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

        # Tasks
        if self.tasks:
            group_elt = etree.SubElement(project_elt, 'tasks')
            for task in sorted(self.tasks, key=lambda k: k.task_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Task: %s ' % task.label)))
                group_elt.append(task.xml())

        # Packs
        if self.packs:
            group_elt = etree.SubElement(project_elt, 'packs')
            for pack in sorted(self.packs, key=lambda k: k.pack_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Pack: %s ' % pack.label)))
                group_elt.append(pack.xml())

        # Team
        self._xml_team(project_elt)

        return project_elt

    # -------------------------------------------------------------------------
    @classmethod
    def team_query(cls, project_id):
        """Query to retrieve ID, login and name of each member of the project
        ``project_id``.

        :param project_id: (integer)
            Project ID.
        :return: (:class:`sqlalchemy.orm.query.Query` instance)
        """
        groups = DBSession.query(ProjectGroup.group_id).filter_by(
            project_id=project_id).all()
        query = DBSession.query(User.user_id, User.login, User.name)
        if groups:
            query = query.filter(or_(
                and_(ProjectUser.project_id == project_id,
                     ProjectUser.user_id == User.user_id),
                and_(GROUPS_USERS.c.group_id.in_(groups),
                     GROUPS_USERS.c.user_id == User.user_id)))\
                .distinct(User.user_id, User.login, User.name)
        else:
            query = query.join(ProjectUser)\
                .filter(ProjectUser.project_id == project_id)
        query = query.filter(User.status == 'active')

        return query

    # -------------------------------------------------------------------------
    @classmethod
    def _load_team(cls, project, roles, project_elt):
        """Load users and groups for project.

        :param project: (:class:`Project` instance)
            SQLAlchemy-powered Project object.
        :param roles: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
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
                    if item.get('roles'):
                        DBSession.flush()
                        for role in item.get('roles').split():
                            DBSession.add(RoleUser(
                                project.project_id, roles[role], user.user_id))
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
                    project.groups.append(
                        ProjectGroup(
                            project.project_id, group.group_id,
                            item.get('permission', 'user')))

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
            roles = DBSession.query(RoleUser.role_id).filter_by(
                project_id=self.project_id, user_id=user.user_id).all()
            if roles:
                elt.set('roles', ' '.join([
                    'rol%d.%d' % (self.project_id, k[0]) for k in roles]))

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

    project_id = Column(
        types.Integer, ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    user_id = Column(
        types.Integer, ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True)
    in_menu = Column(types.Boolean(), default=False)
    perm = Column(
        types.Enum(*PROJECT_PERMS.keys() + ['none'], name='prj_perms_enum'))
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, user_id, in_menu=False, perm='user'):
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

    project_id = Column(
        types.Integer, ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    group_id = Column(
        types.String(ID_LEN),
        ForeignKey('groups.group_id', ondelete='CASCADE'), primary_key=True)
    perm = Column(
        types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'),
        default='user')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, group_id, perm=None):
        """Constructor method."""
        self.project_id = project_id
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm
