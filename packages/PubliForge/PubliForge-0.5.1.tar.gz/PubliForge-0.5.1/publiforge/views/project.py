# $Id: project.py ada86c3ea608 2012/03/22 22:52:47 patrick $
# pylint: disable = I0011, C0322
"""Project view callables."""

from os.path import join, dirname, basename, commonprefix, relpath
from colander import Mapping, SchemaNode, Length, String, OneOf, Date
import zipfile
import tempfile
from sqlalchemy import select, desc, or_, and_

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ..lib.utils import _, has_permission
from ..lib.xml import load, upload_configuration, export_configuration
from ..lib.views import get_action, paging_users, paging_groups
from ..lib.views import current_storage, current_project, file_download
from ..lib.form import Form
from ..lib.renderer import Paging, TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN, DBSession, close_dbsession
from ..models.users import User
from ..models.groups import GROUPS_USERS, Group
from ..models.projects import PROJECT_STATUS, PROJECT_PERMS, Project
from ..models.projects import ProjectUser, ProjectGroup
from ..models.projects import ProjectProcessing, ProjectPack


PROJECT_SETTINGS_TABS = (
    _('Description'), _('Processings'), _('Members'), _('Member groups'))


# =============================================================================
class ProjectView(object):
    """Class to manage projects."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='project_admin',
                 renderer='../Templates/prj_admin.pt',
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
            'i_editor':  has_permission(self._request, 'prj_editor'),
            'i_manager': has_permission(self._request, 'prj_manager')}

    # -------------------------------------------------------------------------
    @view_config(route_name='project_index',
                 renderer='../Templates/prj_index.pt',
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
                project_user = ProjectUser(action[4:], user_id)
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
    @view_config(route_name='project_view',
                 renderer='../Templates/prj_view.pt',
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
            .filter(ProjectUser.perm != None).order_by(User.login)
        member_groups = DBSession.query(
            Group.group_id, Group.label, ProjectGroup.perm)\
            .filter(ProjectGroup.project_id == project.project_id)\
            .filter(Group.group_id == ProjectGroup.group_id)\
            .order_by(Group.label).all()
        i_editor = has_permission(self._request, 'prj_editor') \
            or self._request.session['project']['perm'] == 'editor'

        self._request.breadcrumbs.add(
            _('Project settings'), replace=self._request.route_path(
            'project_edit', project_id=project.project_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'PROJECT_STATUS': PROJECT_STATUS, 'perms': PROJECT_PERMS,
            'project': project, 'members': members,
            'member_groups': member_groups, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(route_name='project_create',
                 renderer='../Templates/prj_edit.pt',
                 permission='prj.create')
    def create(self):
        """Create a project."""
        form, tab_set = self._settings_form()

        if form.validate():
            label = ' '.join(form.values['label'].split()).strip()
            project = DBSession.query(Project).filter_by(label=label).first()
            if project is None:
                project = Project(label, form.values['description'],
                    form.values['status'], form.values['deadline'])
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
    @view_config(route_name='project_edit',
                 renderer='../Templates/prj_edit.pt')
    def edit(self):
        """Edit project settings."""
        # Authorization
        project = current_project(self._request, only_dict=False)
        if not has_permission(self._request, 'prj_editor') \
               and self._request.session['project']['perm'] != 'editor':
            raise HTTPForbidden()

        # Action
        action = get_action(self._request)[0]
        paging = groups = None
        if action == 'aur?' or \
               (not action and self._request.GET.get('paging_id') == 'users'):
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
        elif action == 'agp?' or (not action and
                self._request.GET.get('paging_id') == 'groups'):
            paging = paging_groups(self._request)[0]
        elif action[0:4] == 'agp!':
            self._add_member_groups(project)
        elif action[0:4] == 'rgp!':
            del self._request.session['menu']
            DBSession.query(ProjectUser).filter_by(
                project_id=project.project_id, user_id=int(action[4:]),
                perm=None).delete()
            DBSession.query(ProjectGroup).filter_by(
                project_id=project.project_id, group_id=action[4:]).delete()
            DBSession.commit()
        elif action == 'imp!':
            self._upload_processing(project.project_id)
        elif action[0:4] == 'del!':
            DBSession.query(ProjectProcessing).filter_by(
                project_id=project.project_id, processing_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            if  'container' in self._request.session:
                del self._request.session['container']

        # Environment
        form, tab_set = self._settings_form(project)
        members = DBSession.query(
            User.user_id, User.login, User.name, ProjectUser.perm)\
            .filter(ProjectUser.project_id == project.project_id)\
            .filter(User.user_id == ProjectUser.user_id)\
            .order_by(User.login).all()
        member_groups = DBSession.query(
            Group.group_id, Group.label, ProjectGroup.perm)\
            .filter(ProjectGroup.project_id == project.project_id)\
            .filter(Group.group_id == ProjectGroup.group_id)\
            .order_by(Group.label).all()

        # Save
        view_path = self._request.route_path('project_view',
            project_id=project.project_id)
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
            'member_groups': member_groups, 'paging': paging, 'groups': groups}

    # -------------------------------------------------------------------------
    @view_config(route_name='project_dashboard',
                 renderer='../Templates/prj_dashboard.pt',
                 permission='prj.read')
    def dashboard(self):
        """Display a project dashboard."""
        project = current_project(self._request)
        action, items = get_action(self._request)
        if action[0:4] == 'bld!':
            return HTTPFound(self._request.route_path('build_launch',
                project_id=self._request.matchdict.get('project_id'),
                processing_id=self._request.params['processing_id'],
                pack_ids='_'.join(items)))
        elif action[0:4] == 'del!':
            DBSession.query(ProjectPack)\
                .filter_by(project_id=project['project_id'])\
                .filter(ProjectPack.pack_id.in_(items)).delete('fetch')
            DBSession.commit()
            action = ''

        paging, defaults = self._paging_packs(project['project_id'])
        defaults['processing_id'] = project['processing_id']
        form = Form(self._request, defaults=defaults)

        self._request.breadcrumbs.add(_('Dashboard'), 2)
        return {
            'form': form, 'paging': paging, 'action': action,
            'project': project}

    # -------------------------------------------------------------------------
    @view_config(route_name='project_results',
                 renderer='../Templates/prj_results.pt',
                 permission='prj.read')
    def results(self):
        """List all builds in progress or with result."""
        # Build parameters
        project = current_project(self._request)
        build_list = self._request.registry['fbuild']\
                     .build_list(project['project_id'])
        working = prgrss = users = processings = packs = status_label = None
        if build_list:
            users = [k['user_id'] for k in build_list]
            users = dict(DBSession.query(User.user_id, User.name)
                         .filter(User.user_id.in_(users)).all())
            processings = [k['processing_id'] for k in build_list]
            processings = DBSession.query(ProjectProcessing)\
              .filter_by(project_id=project['project_id'])\
              .filter(ProjectProcessing.processing_id.in_(processings)).all()
            processings = dict([
                (k.processing_id, (k.label, k.output)) for k in processings])
            packs = [k['pack_id'] for k in build_list]
            packs = dict(DBSession.query(
                ProjectPack.pack_id, ProjectPack.label)
                         .filter_by(project_id=project['project_id'])
                         .filter(ProjectPack.pack_id.in_(packs)).all())
            status_label = {'none':  _('In progress...'), 'stop': _('Stopped'),
                            'end': _('Completed'), 'fatal': _('In error')}
            working, prgrss = self._request.registry['fbuild'].progress(
                self._request, [k['build_id'] for k in build_list])

        # Action
        form = Form(self._request)
        action, items = get_action(self._request)
        if action[0:4] == 'dnl!':
            action = self._download_results(build_list, processings, items)
            if action is not None:
                return action

        # Refresh
        if working and not 'ajax' in self._request.params:
            self._request.response.headerlist.append(('Refresh',
                self._request.registry.settings.get('refresh.long', '8')))

        self._request.breadcrumbs.add(_('Results'))
        return {
            'form': form, 'working': working, 'project': project,
            'results': build_list, 'progress': prgrss, 'users': users,
            'processings': processings, 'packs': packs,
            'status_label': status_label}

    # -------------------------------------------------------------------------
    @view_config(route_name='project_results_ajax', renderer='json',
                 permission='prj.read')
    def results_ajax(self):
        """List all builds in progress for AJAX request."""
        project_id = int(self._request.matchdict['project_id'])
        build_list = self._request.registry['fbuild'].build_list(project_id)
        working, prgrss = self._request.registry['fbuild'].progress(
            self._request, [k['build_id'] for k in build_list])
        response = dict([(k, prgrss[k][1]) for k in prgrss])
        response['working'] = working
        return response

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
                select([GROUPS_USERS], user_id == GROUPS_USERS.c.user_id))]
            if groups:
                query = query.filter(or_(
                    and_(ProjectUser.user_id == user_id,
                         ProjectUser.perm != None,
                         ProjectUser.project_id == Project.project_id),
                    and_(ProjectGroup.group_id.in_(groups),
                         ProjectGroup.project_id == Project.project_id))
                    ).distinct(Project.project_id, Project.label)
            else:
                query = query.join(ProjectUser)\
                       .filter(ProjectUser.user_id == user_id)\
                       .filter(ProjectUser.perm != None)
        elif 'f_login' in params:
            query = query.join(ProjectUser).join(User)\
                    .filter(User.login == params['f_login'])\
                    .filter(ProjectUser.perm != None)
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
    def _paging_packs(self, project_id):
        """Return a :class:`~..lib.renderer.Paging` object filled with packs
        of project ``project_id``.

        :param project_id: (integer)
            Project ID.
        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.renderer.Paging` object and ``filters`` a
            dictionary of filters.
        """
        # Parameters
        params = Paging.params(self._request, 'packs', '+pack_id')

        # Query
        query = DBSession.query(ProjectPack).filter_by(project_id=project_id)
        if 'f_label' in params:
            query = query.filter(
                ProjectPack.label.ilike('%%%s%%' % params['f_label']))

        # Order by
        oby = 'projects_packs.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'packs', query), params

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

        tree = load(upload.filename, {'publiforge':
            join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')},
            upload.file.read())
        if isinstance(tree, basestring):
            self._request.session.flash(tree, 'alert')
            return

        error = ProjectProcessing.load(project_id, tree.find('processing'))
        if error is not None:
            self._request.session.flash(error, 'alert')

    # -------------------------------------------------------------------------
    def _settings_form(self, project=None):
        """Return a project settings form.

        :param project: (:class:`~..models.projects.Project` instance,
            optional) Current project object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        schema.add(SchemaNode(String(), name='status',
            validator=OneOf(PROJECT_STATUS.keys())))
        schema.add(SchemaNode(Date(), name='deadline', missing=None))
        if project is not None:
            for user in project.users:
                schema.add(SchemaNode(String(), name='usr_%d' % user.user_id,
                validator=OneOf(PROJECT_PERMS.keys())))
            for group in project.groups:
                schema.add(SchemaNode(String(), name='grp_%s' % group.group_id,
                validator=OneOf(PROJECT_PERMS.keys())))

        defaults = {'status': 'draft'}

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=project),
            TabSet(self._request, PROJECT_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _save(self, project, values):
        """Save a project settings.

        :param project: (:class:`~..models.projects.Project` instance)
            Project to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        i_editor = has_permission(self._request, 'prj_editor')
        for user in project.users:
            if i_editor or user.user_id != self._request.session['user_id']:
                user.perm = values['perm_%d' % user.user_id]

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
        if not has_permission(self._request, 'prj_modifier') \
               and self._request.session['project']['perm'] != 'editor':
            return

        user_ids = [k.user_id for k in project.users]
        for user_id in get_action(self._request)[1]:
            user_id = int(user_id)
            if not user_id in user_ids:
                project.users.append(ProjectUser(user_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _add_member_groups(self, project):
        """Add selected groups to the project.

        :param project_id: (:class:`~..models.projects.Project` instance)
            Project object.
        """
        if not has_permission(self._request, 'prj_editor') \
               and self._request.session['project']['perm'] != 'editor':
            return

        group_ids = [k.group_id for k in project.groups]
        for group_id in get_action(self._request)[1]:
            if not group_id in group_ids:
                project.groups.append(ProjectGroup(
                    project.project_id, group_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _download_results(self, build_list, processings, build_ids):
        """Gather results in a ZIP file and return a Pyramid response.

        :param build_list: (list)
            List of builds of current project.
        :param processings: (dictionary)
            Dictionary of used processings.
        :param build_ids: (list)
            List of build IDs to download.
        :return: (:class:`pyramid.response.Response` instance or raise a
            :class:`pyramid.httpexceptions.HTTPNotFound` exception.)
        """
        # Create file list
        filenames = []
        for build in build_list:
            if build['build_id'] in build_ids and build.get('files'):
                path = processings[build['processing_id']][1]
                if current_storage(self._request, path.partition('/')[0]):
                    filenames += [join(path, k) for k in build['files']]

        # Empty list
        if not filenames:
            self._request.session.flash(_('No result to download!'), 'alert')
            return

        # Single file
        storage_root = self._request.registry.settings['storage.root']
        if len(filenames) == 1:
            return file_download(
                self._request, storage_root, filenames, basename(filenames[0]))

        # Several filenames
        tmp = tempfile.NamedTemporaryFile(
            dir=self._request.registry.settings['temporary_dir'])
        zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        root = join(storage_root, commonprefix(filenames))
        for name in filenames:
            name = join(storage_root, name)
            zip_file.write(name, relpath(name, root))
        zip_file.close()
        return file_download(self._request, '', (tmp.name,), 'results.zip')
