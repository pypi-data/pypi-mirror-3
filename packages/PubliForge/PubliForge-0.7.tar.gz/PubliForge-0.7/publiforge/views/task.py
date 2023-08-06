# $Id: task.py 207bde7ec174 2012/09/05 16:19:37 patrick $
# pylint: disable = I0011, C0322
"""Task view callables."""

from sqlalchemy import func, desc, and_, or_
from colander import Mapping, SchemaNode, Length, OneOf, String, Date
from time import time

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPNotFound

from ..lib.utils import _, has_permission, MIME_TYPES, normalize_spaces, age
from ..lib.utils import rst2xhtml
from ..lib.views import get_action, current_storage, file_details
from ..lib.views import current_project, file_upload
from ..lib.views import operator_label, operator_labels, pack2task
from ..lib.form import Form
from ..lib.renderer import Paging, TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN, DBSession, close_dbsession
from ..models.projects import Project
from ..models.roles import RoleUser
from ..models.packs import Pack, PackEvent
from ..models.tasks import LINK_TYPES, Task, TaskProcessing, TaskLink


TASK_SETTINGS_TABS = (_('Description'), _('Processings'), _('Connections'))


# =============================================================================
class TaskView(object):
    """Class to manage tasks."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='task_index', renderer='../Templates/tsk_index.pt')
    @view_config(
        route_name='task_index_task', renderer='../Templates/tsk_index.pt')
    @view_config(
        route_name='task_index_task_pack',
        renderer='../Templates/tsk_index.pt')
    def index(self):
        """List tasks to do."""
        # Current task and its packs
        project = current_project(self._request)
        current_task = self._current_task(
            project['project_id'], project['perm'] == 'leader'
            and self._request.params.get('f_operator'))

        # Form
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='target', missing=None))
        schema.add(SchemaNode(String(), name='note', missing=None))
        schema.add(SchemaNode(String(), name='message', missing=None))
        defaults = Paging.params(self._request, 'task_packs', '+updated')
        defaults['processing_id'] = project['processing_id']
        defaults['f_operator'] = current_task['operator_id']
        defaults['target'] = current_task['target']
        form = Form(self._request, schema=schema, defaults=defaults)

        # List of operators
        operators = project['perm'] == 'leader' and [(
            k[0], k[2]) for k in Project.team_query(project['project_id'])]

         # Action
        storage = None
        action, items = self._action_index(
            project, current_task, operators, form)
        if action[0:4] == 'bld!':
            return HTTPFound(self._request.route_path(
                'build_launch', project_id=project['project_id'],
                processing_id=project['processing_id'],
                pack_ids='_'.join(items)))
        elif action[0:4] == 'upl?':
            storage = current_storage(
                self._request, action[4:].split('/')[0])[0]

        # List of tasks
        tasks = DBSession.query(
            Task.task_id, Task.label, Task.deadline, func.count(Pack.task_id))\
            .join(Pack).filter(Task.project_id == project['project_id'])\
            .order_by(Task.label)
        if current_task['operator_roles']:
            tasks = tasks.filter(or_(
                and_(Pack.operator_type == 'user',
                     Pack.operator_id == current_task['operator_id']),
                and_(Pack.operator_type == 'role',
                     Pack.operator_id.in_(current_task['operator_roles']))))
        else:
            tasks = tasks.filter(
                Pack.operator_type == 'user',
                Pack.operator_id == current_task['operator_id'])
        tasks = tasks.group_by(Task.task_id, Task.label, Task.deadline).all()

        # List of packs and builds
        packs = self._paging_packs(current_task, defaults)
        builds = packs and self._builds(
            project['project_id'], [k.pack_id for k in packs]) or {}

        # Breadcrumb trail
        if self._request.breadcrumbs.current_path().startswith(
                self._request.route_path(
                    'task_index', project_id=project['project_id'])):
            self._request.breadcrumbs.pop()
        self._request.breadcrumbs.add(_('Tasks'), root_chunks=3)

        return {
            'age': age, 'project': project, 'form': form, 'action': action,
            'operators': operators, 'storage': storage,
            'tasks': tasks, 'current_task': current_task, 'packs': packs,
            'builds': builds, 'MIME_TYPES': MIME_TYPES, 'rst2xhtml': rst2xhtml}

    # -------------------------------------------------------------------------
    @view_config(route_name='task_view', renderer='../Templates/tsk_view.pt')
    def view(self):
        """Display task settings."""
        # Permission
        project = current_project(self._request)
        task = DBSession.query(Task).filter_by(
            task_id=int(self._request.matchdict.get('task_id'))).first()
        if task is None:
            raise HTTPNotFound()
        tab_set = TabSet(self._request, TASK_SETTINGS_TABS)
        operator = operator_label(
            self._request, project, task.operator_type, task.operator_id)
        i_editor = project['perm'] == 'leader' \
            or has_permission(self._request, 'prj_editor')

        self._request.breadcrumbs.add(
            _('Task settings'), replace=self._request.route_path(
                'task_edit', project_id=task.project_id, task_id=task.task_id))

        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'project': project, 'task': task, 'operator': operator,
            'i_editor': i_editor, 'LINK_TYPES': LINK_TYPES}

    # -------------------------------------------------------------------------
    @view_config(route_name='task_create', renderer='../Templates/tsk_edit.pt')
    def create(self):
        """Create a task."""
        # Authorization
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Environment
        form, tab_set, operators = self._settings_form(project)

        # Action
        action = get_action(self._request)[0]
        if action == 'sav!' and form.validate():
            task = self._create(project['project_id'], form.values)
            if task is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'task_edit', project_id=task.project_id,
                    task_id=task.task_id))

        self._request.breadcrumbs.add(_('Task creation'))

        return {
            'form': form, 'tab_set': tab_set, 'project': project,
            'task': None, 'operators': operators}

    # -------------------------------------------------------------------------
    @view_config(route_name='task_edit', renderer='../Templates/tsk_edit.pt')
    def edit(self):
        """Edit a task."""
        # Authorization
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Environment
        task = DBSession.query(Task).filter_by(
            project_id=project['project_id'],
            task_id=int(self._request.matchdict.get('task_id'))).first()
        if task is None:
            raise HTTPNotFound()
        form, tab_set, operators = self._settings_form(project, task)

        # Save
        action = self._action(task)
        view_path = self._request.route_path(
            'task_view', project_id=task.project_id, task_id=task.task_id)
        if action == 'sav!' and form.validate(task) \
                and self._save(task, form.values):
            del self._request.session['project']
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Task'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'project': project, 'task': task, 'operators': operators,
            'LINK_TYPES': LINK_TYPES}

    # -------------------------------------------------------------------------
    def _action(self, task):
        """Return current action for edit view.

        :param task: (:class:`~..models.tasks.Task` instance, optional)
            Current task object.
        :return: (string)
            Current action.
        """
        action, items = get_action(self._request)
        # Processings
        if action[0:4] == 'apr!':
            done = [k.processing_id for k in task.processings]
            for item in items:
                item = int(item)
                if not item in done:
                    task.processings.append(TaskProcessing(
                        task.project_id, task.task_id, item))
            DBSession.commit()
        elif action[0:4] == 'rpr!':
            DBSession.query(TaskProcessing).filter_by(
                project_id=task.project_id, task_id=task.task_id,
                processing_id=int(action[4:])).delete()
            DBSession.commit()
        # Links
        if action[0:4] == 'alk!':
            done = [k.target_id for k in task.links]
            for item in items:
                item = int(item)
                if not item in done:
                    task.links.append(TaskLink(
                        task.project_id, task.task_id, item))
            DBSession.commit()
        elif action[0:4] == 'rlk!':
            DBSession.query(TaskLink).filter_by(
                project_id=task.project_id, task_id=task.task_id,
                target_id=int(action[4:])).delete()
            DBSession.commit()

        return action

    # -------------------------------------------------------------------------
    def _action_index(self, project, current_task, operators, form):
        """Process action for index view.

        :param project: (dictionary)
            Current project.
        :param current_task: (dictionary)
            Current task.
        :param operators: (list)
            Names of operators.
        :param form: (:class:`~..lib.form.Form` instance)
            Current form.
        :return: (tuple)
            A tuple such as ``(action, items)``
        """
        action, items = get_action(self._request)
        if not form.validate():
            action = '%s?%s' % (action[0:3], action[4:])
        if action[0:4] == 'upl!':
            file_upload(self._request, action[4:], form.values['message'])
            action = ''
        elif action[0:4] in ('nxt!', 'tak!'):
            for pack_id in items:
                pack = DBSession.query(Pack).filter_by(
                    project_id=project['project_id'], pack_id=int(pack_id))\
                    .first()
                if action[0:4] == 'nxt!' and pack.operator_type == 'user':
                    pack2task(
                        self._request, pack,
                        form.values['target'][0:4] == 'back',
                        int(form.values['target'][4:]))
                elif action[0:4] == 'tak!' and pack.operator_type == 'role':
                    pack.operator_type = 'user'
                    pack.operator_id = current_task['operator_id']
                    name = operators and dict(operators)[pack.operator_id] \
                        or self._request.session['name']
                    DBSession.add(PackEvent(
                        project['project_id'], pack.pack_id,
                        current_task['task_id'],
                        project['task_labels'][current_task['task_id']],
                        pack.operator_type, pack.operator_id, name))
                    DBSession.commit()
            form.forget('#')
            action = ''
        elif action[0:4] == 'not!':
            pack = DBSession.query(Pack).filter_by(
                project_id=project['project_id'], pack_id=int(items[0]))\
                .first()
            pack.note = form.values['note'] and form.values['note'].strip() \
                or None
            DBSession.commit()
            action = ''

        return action, items

    # -------------------------------------------------------------------------
    def _settings_form(self, project, task=None):
        """Return a task settings form.

        :param project: (dictionary)
            Current project dictionary.
        :param task: (:class:`~..models.tasks.Task` instance, optional)
            Current task object.
        :return: (tuple)
             A tuple such as ``(form, tab_set)``
        """
        operators = operator_labels(project, True)
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description', missing='',
            validator=Length(max=DESCRIPTION_LEN)))
        schema.add(SchemaNode(
            String(), name='operator',
            validator=OneOf([k[0] for k in operators])))
        schema.add(SchemaNode(Date(), name='deadline', missing=None))
        defaults = {}
        if task is not None:
            defaults['operator'] = '%s%s' % (
                task.operator_type, str(task.operator_id))
            for link in task.links:
                schema.add(SchemaNode(
                    String(), name='lnk_%d' % link.target_id,
                    validator=OneOf(LINK_TYPES.keys())))

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=task),
            TabSet(self._request, TASK_SETTINGS_TABS), operators)

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``projects_tasks`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return:
            (:class:`~..models.tasks.Task` instance)
        """
        # Check unicity
        label = normalize_spaces(values['label'], LABEL_LEN)
        task = DBSession.query(Task).filter_by(
            project_id=project_id, label=label).first()
        if task is not None:
            self._request.session.flash(
                _('This task already exists.'), 'alert')
            return

        # Create task
        task = Task(
            project_id, label, values['description'], values['deadline'])
        DBSession.add(task)
        DBSession.commit()

        return task

    # -------------------------------------------------------------------------
    @classmethod
    def _save(cls, task, values):
        """Save task settings.

        :param project: (:class:`~..models.tasks.Task` instance)
            Task to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Operator
        task.operator_type = values['operator'][0:4]
        task.operator_id = task.operator_type != 'auto' \
            and int(values['operator'][4:]) or None

        # Links
        for link in task.links:
            link.link_type = values['lnk_%d' % link.target_id]

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    def _current_task(self, project_id, operator_id=None):
        """Initialize, if necessary, ``request.session['task']`` and return it
        as current task dictionary.

        :param project_id: (string)
            Project ID.
        :param operator_id: (string, default=current user ID)
            Operator ID.
        :return: (dictionary)
            The dictionary has the following keys: ``project_id``, ``task_id``,
            ``operator_id``, ``operator_roles``, ``description``,
            ``new_task``, ``processing_ids``, ``targets``, ``target``,
            ``pack_id`` and ``files``.
        """
        # Task dictionary
        if 'task' not in self._request.session \
                or self._request.session['task']['project_id'] != project_id:
            self._request.session['task'] = {
                'project_id': project_id, 'task_id': None, 'operator_id': None,
                'pack_id': None, 'target': None}
        task_dict = self._request.session['task']

        # Task
        task_id = self._request.matchdict.get('task_id')
        task_id = task_id is not None and int(task_id) or None
        task_dict['new_task'] = task_id is not None \
            and task_id != task_dict['task_id']
        if task_id is not None or self._request.GET.get('close_task'):
            task_dict['task_id'] = task_id
        if task_dict['task_id'] is not None and task_dict['new_task']:
            record = DBSession.query(Task).filter_by(
                project_id=project_id, task_id=task_dict['task_id']).first()
            if record is None:
                raise HTTPNotFound(comment=_('This task does not exist!'))
            task_dict['description'] = record.description
            task_dict['processing_ids'] = [
                k.processing_id for k in record.processings]
            task_dict['targets'] = [
                '%s%d' % (k.link_type[0:4], k.target_id) for k in record.links]
        if task_dict['task_id'] is None:
            task_dict['description'] = None
            task_dict['processing_ids'] = []
            task_dict['targets'] = []
        if self._request.params.get('target'):
            task_dict['target'] = self._request.params.get('target')

        # Operator
        operator_id = operator_id and int(operator_id) \
            or task_dict['operator_id'] or self._request.session['user_id']
        if task_dict['operator_id'] != operator_id:
            task_dict['operator_id'] = operator_id
            task_dict['operator_roles'] = tuple([
                k[0] for k in DBSession.query(RoleUser.role_id).filter(
                    RoleUser.project_id == project_id,
                    RoleUser.user_id == operator_id)])

        # Pack with files
        pack_id = self._request.matchdict.get('pack_id')
        pack_id = pack_id is not None and int(pack_id) or None
        new_pack = pack_id is not None \
            and pack_id != task_dict['pack_id']
        if pack_id is not None or self._request.GET.get('close_pack'):
            task_dict['pack_id'] = pack_id
        if task_dict['pack_id'] is not None and new_pack:
            record = DBSession.query(Pack).filter_by(
                project_id=project_id, pack_id=task_dict['pack_id']).first()
            task_dict['files'] = file_details(self._request, record)
            self._request.session['container'] = {
                'project_id': project_id, 'pack_id': task_dict['pack_id'],
                'pack_label': record.label}
        if task_dict['pack_id'] is None:
            task_dict['files'] = []

        return task_dict

    # -------------------------------------------------------------------------
    def _paging_packs(self, task, filters):
        """Return a :class:`~..lib.renderer.Paging` object filled with packs of
        project ``project_id`` currently used by task
        ``current_task['task_id']``.

        :param task: (dictionary)
            Current task dictionary.
        :param filters: (dictionary)
            Filters for pack list.
        :return: (:class:`~..lib.renderer.Paging` instance)
        """
        if task['task_id'] is None:
            return None

        # Query
        query = DBSession.query(Pack).filter_by(
            project_id=task['project_id'], task_id=task['task_id'])
        if task['operator_roles']:
            query = query.filter(or_(
                and_(Pack.operator_type == 'user',
                     Pack.operator_id == task['operator_id']),
                and_(Pack.operator_type == 'role',
                     Pack.operator_id.in_(task['operator_roles']))))
        else:
            query = query.filter_by(
                operator_type='user', operator_id=task['operator_id'])
        if 'f_label' in filters:
            query = query.filter(
                Pack.label.ilike('%%%s%%' % filters['f_label']))

        # Order by
        oby = 'packs.%s' % filters['sort'][1:]
        query = query.order_by(desc(oby) if filters['sort'][0] == '-' else oby)

        return Paging(self._request, 'task_packs', query)

    # -------------------------------------------------------------------------
    def _builds(self, project_id, pack_ids):
        """Return error messages of builds on packs ``packs``.

        :param project_id: (string)
            Project ID.
        :param pack_ids: (list)
            Visible pack IDs.
        :return: (dictionary)
            A dictionary such as ``{pack_id: (build_id, message),...}``.
        """
        builds = {}
        expire = time() - 5 * int(self._request.registry.settings.get(
            'storage.report_ttl', 12))
        for build in self._request.registry['fbuild'].build_list(
                project_id, self._request.session['user_id']):
            if build['pack_id'] not in pack_ids or build['pack_id'] in builds \
                    or build['status'] == 'end':
                continue
            result = self._request.registry['fbuild'].result(build['build_id'])
            if result.get('message') and result['log'][-1][0] > expire:
                builds[build['pack_id']] = (
                    build['build_id'], result['message'])

        return builds
