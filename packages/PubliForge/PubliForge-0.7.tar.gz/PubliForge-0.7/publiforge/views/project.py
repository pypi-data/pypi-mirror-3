# $Id: project.py 4c5a8816200c 2012/09/06 09:04:56 patrick $
# pylint: disable = I0011, C0322
"""Project view callables."""

from os.path import join, dirname
from colander import Mapping, SchemaNode, Length, String, OneOf, Date
from sqlalchemy import select, desc, or_, and_
from webhelpers.html import literal

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.i18n import get_localizer

from ..lib.utils import _, has_permission, normalize_spaces
from ..lib.xml import load, upload_configuration, export_configuration
from ..lib.views import get_action, paging_users, paging_groups
from ..lib.views import current_project, operator_labels
from ..lib.form import Form
from ..lib.renderer import Paging, TabSet
from ..models import NULL, LABEL_LEN, DESCRIPTION_LEN
from ..models import DBSession, close_dbsession
from ..models.users import User
from ..models.groups import GROUPS_USERS, Group
from ..models.projects import PROJECT_STATUS, PROJECT_PERMS, Project
from ..models.projects import ProjectUser, ProjectGroup
from ..models.processings import Processing, ProcessingVariable
from ..models.processings import ProcessingUserVariable
from ..models.roles import Role
from ..models.tasks import Task, TaskLink
from ..models.packs import Pack

PROJECT_SETTINGS_TABS = (
    _('Description'), _('Roles'), _('Processings'), _('Tasks'),
    _('Direct members'), _('Member groups'))


# =============================================================================
class ProjectView(object):
    """Class to manage projects."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_admin', renderer='../Templates/prj_admin.pt',
        permission='prj.update')
    def admin(self):
        """List projects for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'prj_manager', 'project')
            action = ''
        elif action[0:4] == 'del!':
            self._delete_projects(items)
            action = ''
        elif action[0:4] == 'exp!':
            return self._export_projects(items)

        paging, defaults = self._paging_projects()
        form = Form(self._request, defaults=defaults)
        groups = [(k.group_id, k.label) for k in
                  DBSession.query(Group).join(ProjectGroup)]

        depth = (self._request.breadcrumbs.current_path() ==
                 self._request.route_path('site_admin') and 3) or 2
        self._request.breadcrumbs.add(_('Project administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action,
            'groups': groups, 'project_status': PROJECT_STATUS,
            'i_editor': has_permission(self._request, 'prj_editor'),
            'i_manager': has_permission(self._request, 'prj_manager')}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_index', renderer='../Templates/prj_index.pt',
        permission='prj.read')
    def index(self):
        """List authorized projects."""
        action, items = get_action(self._request)
        if action[0:4] == 'exp!':
            return self._export_projects(items)
        elif action[0:3] == 'men':
            user_id = self._request.session['user_id']
            project_user = DBSession.query(ProjectUser).filter_by(
                project_id=action[4:], user_id=user_id).first()
            if project_user is None:
                project_user = ProjectUser(action[4:], user_id, perm='none')
                DBSession.add(project_user)
            project_user.in_menu = action[3] == '+'
            DBSession.commit()
            del self._request.session['menu']

        paging, defaults = self._paging_projects(
            self._request.session['user_id'])
        form = Form(self._request, defaults=defaults)
        in_menus = [k[0] for k in DBSession.query(ProjectUser.project_id)
                    .filter_by(user_id=self._request.session['user_id'])
                    .filter_by(in_menu=True).all()]

        if 'container' in self._request.session:
            del self._request.session['container']

        self._request.breadcrumbs.add(_('All projects'), 2)
        return {
            'form': form, 'paging': paging, 'action': action,
            'project_status': PROJECT_STATUS, 'in_menus': in_menus}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_view', renderer='../Templates/prj_view.pt',
        permission='prj.read')
    def view(self):
        """Show project settings with its users."""
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_projects((
                self._request.matchdict.get('project_id'),))

        project = current_project(self._request, only_dict=False)
        tab_set = TabSet(self._request, PROJECT_SETTINGS_TABS)
        members = DBSession.query(
            User.user_id, User.login, User.name, ProjectUser.perm)\
            .join(ProjectUser)\
            .filter(ProjectUser.project_id == project.project_id)\
            .filter(ProjectUser.perm != NULL).order_by(User.name).all()
        member_groups = DBSession.query(
            Group.group_id, Group.label, ProjectGroup.perm)\
            .filter(ProjectGroup.project_id == project.project_id)\
            .filter(Group.group_id == ProjectGroup.group_id)\
            .order_by(Group.label).all()
        i_editor = self._request.session['project']['perm'] == 'leader' \
            or has_permission(self._request, 'prj_editor')

        self._request.breadcrumbs.add(
            _('Project settings'), replace=self._request.route_path(
                'project_edit', project_id=project.project_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'PROJECT_STATUS': PROJECT_STATUS, 'perms': PROJECT_PERMS,
            'project': project, 'members': members,
            'member_groups': member_groups, 'i_editor': i_editor,
            'operator_labels': dict(operator_labels(
                self._request.session['project'], True))}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_create', renderer='../Templates/prj_edit.pt',
        permission='prj.create')
    def create(self):
        """Create a project."""
        form, tab_set = self._settings_form()

        if form.validate():
            label = normalize_spaces(form.values['label'])
            project = DBSession.query(Project).filter_by(label=label).first()
            if project is None:
                project = Project(
                    label, form.values['description'], form.values['status'],
                    form.values['deadline'])
                DBSession.add(project)
                DBSession.commit()
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'project_edit', project_id=project.project_id))
            self._request.session.flash(
                _('This label already exists.'), 'alert')

        self._request.breadcrumbs.add(_('Project creation'))
        return{
            'form': form, 'tab_set': tab_set,
            'PROJECT_STATUS': PROJECT_STATUS, 'perms': PROJECT_PERMS,
            'project': None, 'members': None, 'group_members': None,
            'paging': None, 'groups': None}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_edit', renderer='../Templates/prj_edit.pt')
    def edit(self):
        """Edit project settings."""
        # Authorization
        project = current_project(self._request, only_dict=False)
        if self._request.session['project']['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Action
        action, paging, groups = self._action(project)

        # Environment
        form, tab_set = self._settings_form(project)
        members = DBSession.query(
            User.user_id, User.login, User.name, ProjectUser.perm)\
            .filter(ProjectUser.project_id == project.project_id)\
            .filter(User.user_id == ProjectUser.user_id)\
            .order_by(User.name).all()
        member_groups = DBSession.query(
            Group.group_id, Group.label, ProjectGroup.perm)\
            .filter(ProjectGroup.project_id == project.project_id)\
            .filter(Group.group_id == ProjectGroup.group_id)\
            .order_by(Group.label).all()

        # Save
        view_path = self._request.route_path(
            'project_view', project_id=project.project_id)
        if action == 'sav!' and form.validate(project) \
                and self._save(project, form.values):
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Project settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'PROJECT_STATUS': PROJECT_STATUS, 'perms': PROJECT_PERMS,
            'project': project, 'members': members,
            'member_groups': member_groups, 'paging': paging, 'groups': groups,
            'operator_labels': dict(operator_labels(
                self._request.session['project'], True))}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='project_dashboard',
        renderer='../Templates/prj_dashboard.pt', permission='prj.read')
    def dashboard(self):
        """Display a project dashboard."""
        project = current_project(self._request)
        pid = project['project_id']
        route = self._request.route_path

        # Tasks
        packs = DBSession.query(
            Pack.pack_id, Pack.task_id, Pack.operator_type, Pack.operator_id)\
            .filter_by(project_id=pid).all()
        count = [k[1] for k in packs if k[1] is not None and k[2] == 'user'
                 and k[3] == self._request.session['user_id']]
        count = len(set(count)), len(count)
        label = (count[0] > 1 and count[1] > 1 and _(
            '${t} tasks on ${p} packs', {'t': count[0], 'p': count[1]})) \
            or (count[0] == 1 and count[1] > 1 and
                _('1 task on ${p} packs', {'p': count[1]})) \
            or (count[0] == 1 and _('1 task on 1 pack')) or _('No task')
        count = len([k[0] for k in packs
                     if k[2] == 'role' and k[3] in project['my_roles']])
        if count:
            translate = get_localizer(self._request).translate
            label = literal(
                translate(label) + '<br/>' + translate(
                    (count > 1 and _('${p} packs to accept', {'p': count}))
                    or (count == 1 and _('1 pack to accept'))))
        entries = [('task', route('task_index', project_id=pid), label)]

        # Packs
        count = len(packs)
        label = (count > 1 and _('${p} packs', {'p': count})) \
            or (count == 1 and _('1 pack')) or _('No pack')
        entries += [('pack', route('pack_index', project_id=pid), label)]

        # Builds
        count = len(self._request.registry['fbuild'].build_list(
            pid, project['perm'] != 'leader' and
            self._request.session['user_id'] or None))
        label = (count > 1 and _('${b} last results', {'b': count})) \
            or (count == 1 and _('1 last result')) or _('No recent result')
        entries += [('build', route('build_results', project_id=pid), label)]

        self._request.breadcrumbs.add(_('Dashboard'), 2)
        return {'project': project, 'entries': entries}

    # -------------------------------------------------------------------------
    def _action(self, project):
        """Return current action for edit view.

        :param project: (:class:`~.models.projects.Project` instance)
            Current project object.
        :return: (tuple)
            A tuple such as ``(action, paging, groups)``.
        """
        action = get_action(self._request)[0]
        paging = None
        # Member
        if action[0:4] in ('aur?', 'aur!', 'rur!', 'agp?', 'agp!', 'rgp!') \
                or (not action and
                    self._request.GET.get('paging_id') in ('users', 'groups')):
            return self._action_member(project, action)
        # Role
        elif action[0:4] == 'drl!':
            DBSession.query(Role).filter_by(
                project_id=project.project_id, role_id=int(action[4:]))\
                .delete()
            DBSession.commit()
        # Processing
        elif action[0:4] == 'del!':
            DBSession.query(Processing).filter_by(
                project_id=project.project_id, processing_id=int(action[4:]))\
                .delete()
            DBSession.query(ProcessingVariable).filter_by(
                project_id=project.project_id,
                default='prc%d.%s' % (project.project_id, action[4:])).delete()
            DBSession.query(ProcessingUserVariable).filter_by(
                project_id=project.project_id,
                value='prc%d.%s' % (project.project_id, action[4:])).delete()
            DBSession.commit()
            if 'container' in self._request.session:
                del self._request.session['container']
            if 'project' in self._request.session:
                del self._request.session['project']
            current_project(self._request, project.project_id)
        elif action == 'imp!':
            self._upload_processing(project.project_id)
        # Task
        elif action[0:4] == 'dtk!':
            for pack in DBSession.query(Pack).filter_by(
                    project_id=project.project_id, task_id=int(action[4:])):
                pack.task_id = None
            DBSession.query(TaskLink).filter_by(
                project_id=project.project_id, target_id=int(action[4:]))\
                .delete()
            DBSession.query(Task).filter_by(
                project_id=project.project_id, task_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            if 'task' in self._request.session and \
                    self._request.session['task']['task_id'] == \
                    int(action[4:]):
                del self._request.session['task']

        return action, paging, None

    # -------------------------------------------------------------------------
    def _action_member(self, project, action):
        """Return current member or member group action.

        :param project: (:class:`~.models.projects.Project` instance)
            Current project object.
        :return: (tuple)
            A tuple such as ``(action, paging, groups)``.
        """
        # Member
        paging = groups = None
        if action == 'aur?' or (
                not action and self._request.GET.get('paging_id') == 'users'):
            paging = paging_users(self._request)[0]
            groups = DBSession.query(Group.group_id, Group.label).all()
        elif action[0:4] == 'aur!':
            self._add_members(project)
        elif action[0:4] == 'rur!':
            del self._request.session['menu']
            DBSession.query(ProjectUser).filter_by(
                project_id=project.project_id, user_id=int(action[4:]))\
                .delete()
            DBSession.commit()
        # Member group
        elif action == 'agp?' or (
                not action and self._request.GET.get('paging_id') == 'groups'):
            paging = paging_groups(self._request)[0]
        elif action[0:4] == 'agp!':
            self._add_member_groups(project)
        elif action[0:4] == 'rgp!':
            del self._request.session['menu']
            users = [
                k[0] for k in DBSession.query(GROUPS_USERS.c.user_id)
                .filter(GROUPS_USERS.c.group_id == action[4:])]
            DBSession.query(ProjectUser).filter_by(
                project_id=project.project_id, perm=None)\
                .filter(ProjectUser.user_id.in_(users)).delete('fetch')
            DBSession.query(ProjectGroup).filter_by(
                project_id=project.project_id, group_id=action[4:]).delete()
            DBSession.commit()

        return action, paging, groups

    # -------------------------------------------------------------------------
    def _paging_projects(self, user_id=None):
        """Return a :class:`~..lib.renderer.Paging` object filled with
        projects.

        :param user_id: (integer, optional)
            Select only projects of user ``user_id``.
        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.renderer.Paging` object and ``filters`` a
            dictionary of filters.
        """
        # Parameters
        paging_id = user_id is None and 'projects!' or 'projects'
        params = Paging.params(self._request, paging_id, '+label')
        if len(self._request.POST) == 0 and not 'f_status' in params:
            params['f_status'] = 'active'

        # Query
        query = DBSession.query(Project)
        if user_id is not None:
            groups = [k.group_id for k in DBSession.execute(
                select([GROUPS_USERS], user_id == GROUPS_USERS.c.user_id))] \
                if DBSession.query(ProjectGroup).first() else None
            if groups:
                query = query.filter(or_(
                    and_(ProjectUser.user_id == user_id,
                         ProjectUser.perm != NULL,
                         ProjectUser.project_id == Project.project_id),
                    and_(ProjectGroup.group_id.in_(groups),
                         ProjectGroup.project_id == Project.project_id)))\
                    .distinct(Project.project_id, Project.label)
            else:
                query = query.join(ProjectUser)\
                    .filter(ProjectUser.user_id == user_id)\
                    .filter(ProjectUser.perm != NULL)
        elif 'f_login' in params:
            query = query.join(ProjectUser).join(User)\
                .filter(User.login == params['f_login'])\
                .filter(ProjectUser.perm != NULL)
        if 'f_group' in params:
            query = query.join(ProjectGroup).filter(
                ProjectGroup.group_id == params['f_group'])
        if 'f_label' in params:
            query = query.filter(
                Project.label.ilike('%%%s%%' % params['f_label']))
        if 'f_status' in params and params['f_status'] != '*':
            query = query.filter(Project.status == params['f_status'])

        # Order by
        oby = 'projects.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)
        return Paging(self._request, paging_id, query), params

    # -------------------------------------------------------------------------
    def _delete_projects(self, project_ids):
        """Delete projects.

        :param project_ids: (list)
            List of project IDs to delete.
        """
        if not has_permission(self._request, 'prj_manager'):
            raise HTTPForbidden()
        DBSession.query(Project).filter(
            Project.project_id.in_(project_ids)).delete('fetch')
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _export_projects(self, project_ids):
        """Export projects.

        :param project_ids: (list)
            List of project IDs to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        i_editor = has_permission(self._request, 'prj_editor')
        user_id = self._request.session['user_id']
        groups = set([k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))])
        elements = []
        for project in DBSession.query(Project)\
                .filter(Project.project_id.in_(project_ids))\
                .order_by('label'):
            if i_editor or user_id in [k.user_id for k in project.users] \
                    or (groups and
                        groups & set([k.group_id for k in project.groups])):
                elements.append(project.xml(self._request))

        name = '%s_projects.pfp' % self._request.registry.settings.get(
            'skin.label', 'publiforge')
        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _upload_processing(self, project_id):
        """Import processing.

        :param project_id: (string)
            Project ID.
        """
        if not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()
        upload = self._request.params.get('xml_file')
        if isinstance(upload, basestring):
            return

        tree = load(
            upload.filename,
            {'publiforge': join(
                dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')},
            upload.file.read())
        if isinstance(tree, basestring):
            self._request.session.flash(tree, 'alert')
            return

        error = Processing.load(project_id, tree.find('processing'))
        if isinstance(error, basestring):
            self._request.session.flash(error, 'alert')
            return

        if 'project' in self._request.session:
            del self._request.session['project']
        current_project(self._request, project_id)

    # -------------------------------------------------------------------------
    def _settings_form(self, project=None):
        """Return a project settings form.

        :param project: (:class:`~..models.projects.Project` instance,
            optional) Current project object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        schema.add(SchemaNode(
            String(), name='status', validator=OneOf(PROJECT_STATUS.keys())))
        schema.add(SchemaNode(Date(), name='deadline', missing=None))
        if project is not None:
            for user in project.users:
                schema.add(SchemaNode(
                    String(), name='usr_%d' % user.user_id,
                    validator=OneOf(PROJECT_PERMS.keys())))
            for group in project.groups:
                schema.add(SchemaNode(
                    String(), name='grp_%s' % group.group_id,
                    validator=OneOf(PROJECT_PERMS.keys())))

        defaults = {'status': 'draft'}
        if  'paging' in self._request.session:
            if 'users' in self._request.session['paging'][1]:
                defaults.update(self._request.session['paging'][1]['users'])
            if 'groups' in self._request.session['paging'][1]:
                defaults.update(self._request.session['paging'][1]['groups'])

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=project),
            TabSet(self._request, PROJECT_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _save(self, project, values):
        """Save project settings.

        :param project: (:class:`~..models.projects.Project` instance)
            Project to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        for user in project.users:
            if user.user_id != self._request.session['user_id'] \
                    or user.perm != 'leader':
                user.perm = values['usr_%d' % user.user_id]
        for group in project.groups:
            group.perm = values['grp_%s' % group.group_id]

        if 'project' in self._request.session:
            del self._request.session['project']
        if 'build' in self._request.session:
            del self._request.session['build']

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    def _add_members(self, project):
        """Add selected users to the project.

        :param project_id: (:class:`~..models.projects.Project` instance)
            Project object.
        """
        user_ids = [k.user_id for k in project.users]
        for user_id in get_action(self._request)[1]:
            user_id = int(user_id)
            if not user_id in user_ids:
                project.users.append(ProjectUser(project.project_id, user_id))
        DBSession.commit()
        if 'project' in self._request.session:
            del self._request.session['project']
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _add_member_groups(self, project):
        """Add selected groups to the project.

        :param project: (:class:`~..models.projects.Project` instance)
            Project object.
        """
        group_ids = [k.group_id for k in project.groups]
        for group_id in get_action(self._request)[1]:
            if not group_id in group_ids:
                project.groups.append(ProjectGroup(
                    project.project_id, group_id))
        DBSession.commit()
        if 'project' in self._request.session:
            del self._request.session['project']
        del self._request.session['menu']
