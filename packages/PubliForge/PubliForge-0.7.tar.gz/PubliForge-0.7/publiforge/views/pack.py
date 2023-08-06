# $Id: pack.py 77a5c869abcc 2012/09/02 18:01:52 patrick $
# pylint: disable = I0011, C0322
"""Pack view callables."""

from colander import Mapping, SchemaNode, String, Boolean, Integer
from colander import Length, OneOf
from sqlalchemy import desc

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.i18n import get_localizer

from ..lib.utils import _, MIME_TYPES, normalize_spaces, age, rst2xhtml
from ..lib.views import get_action, current_project, file_details
from ..lib.views import operator_label, operator_labels, task_auto_build
from ..lib.form import Form
from ..lib.renderer import Paging, TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.tasks import Task
from ..models.packs import Pack, PackFile, PackEvent


PACK_SETTINGS_TABS = (
    _('Description'), _('Files'), _('Note'), _('Task'), _('History'))
FILE_TYPE_LABELS = {
    'file': _('Files to process'), 'resource': _('Resource files'),
    'template': _('Template files')}


# =============================================================================
class PackView(object):
    """Class to manage packs."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_index', renderer='../Templates/pck_index.pt')
    @view_config(
        route_name='pack_index_pack', renderer='../Templates/pck_index.pt')
    def index(self):
        """List all packs of a project."""
        # List of packs and current pack
        project = current_project(self._request)
        paging, defaults = self._paging_packs(project['project_id'])
        defaults['processing_id'] = project['processing_id']
        pack, files = self._current_pack(project['project_id'])

        # Action
        action, items = get_action(self._request)
        if action[0:4] == 'del!':
            items = [int(k) for k in items]
            if 'container' in self._request.session \
                    and self._request.session['container']['pack_id'] in items:
                del self._request.session['container']
            if 'task' in self._request.session \
                    and self._request.session['task']['pack_id'] in items:
                self._request.session['task']['pack_id'] = None
                self._request.session['task']['files'] = []
            DBSession.query(Pack)\
                .filter_by(project_id=project['project_id'])\
                .filter(Pack.pack_id.in_(items)).delete('fetch')
            DBSession.commit()
            action = ''
        elif action[0:4] == 'bld!':
            return HTTPFound(self._request.route_path(
                'build_launch', project_id=project['project_id'],
                processing_id=project['processing_id'],
                pack_ids='_'.join(items)))

        # Breadcrumb trail
        if self._request.breadcrumbs.current_path().startswith(
                self._request.route_path(
                'pack_index', project_id=project['project_id'])):
            self._request.breadcrumbs.pop()
        self._request.breadcrumbs.add(_('Packs'), root_chunks=3)

        return {
            'form': Form(self._request, defaults=defaults), 'paging': paging,
            'action': action, 'project': project, 'MIME_TYPES': MIME_TYPES,
            'pack_id': pack and pack.pack_id, 'files': files}

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_view', renderer='../Templates/pck_view.pt')
    def view(self):
        """Display a pack."""
        # Environment
        project = current_project(self._request)
        pack, files = self._current_pack(project['project_id'], False)
        tab_set = TabSet(self._request, PACK_SETTINGS_TABS)
        form = Form(self._request,
                    defaults={'processing_id': project['processing_id']})
        operator = pack.task_id and operator_label(
            self._request, project, pack.operator_type, pack.operator_id)

        # Action
        if get_action(self._request)[0] == 'bld!' and form.validate():
            return HTTPFound(self._request.route_path(
                'build_launch', project_id=project['project_id'],
                processing_id=form.values['processing_id'],
                pack_ids=pack.pack_id))

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Pack'), replace=self._request.route_path(
                'pack_edit', project_id=project['project_id'],
                pack_id=pack.pack_id))

        return {
            'age': age, 'form': form, 'tab_set': tab_set, 'project': project,
            'pack': pack, 'files': files, 'file_type_labels': FILE_TYPE_LABELS,
            'MIME_TYPES': MIME_TYPES, 'note': rst2xhtml(pack.note),
            'operator': operator, 'events': self._paging_events(pack)[0]}

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_create', renderer='../Templates/pck_edit.pt')
    def create(self):
        """Create a pack."""
        project = current_project(self._request)
        form, tab_set = self._settings_form(project)[0:2]

        if form.validate():
            pack = self._create(project['project_id'], form.values)
            if pack is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'pack_edit', project_id=pack.project_id,
                    pack_id=pack.pack_id, _anchor='tab1'))

        self._request.breadcrumbs.add(_('Pack creation'))
        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'pack': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_edit', renderer='../Templates/pck_edit.pt')
    def edit(self):
        """Edit a pack."""
        # Environment
        project = current_project(self._request)
        pack, files = self._current_pack(project['project_id'], False)
        form, tab_set, operators = self._settings_form(project, pack)

        # Action
        # pylint: disable = I0011, E1103
        action = get_action(self._request)[0]
        if action[0:4] == 'rmv!':
            DBSession.query(PackFile).filter_by(
                project_id=project['project_id'], pack_id=pack.pack_id,
                file_type=action[4:].partition('_')[0],
                path=action[4:].partition('_')[2]).delete()
            DBSession.commit()
            files = file_details(self._request, pack, False)
            if 'task' in self._request.session and \
                    self._request.session['task']['pack_id'] == pack.pack_id:
                self._request.session['task']['files'] = file_details(
                    self._request, pack)
        elif action == 'sav!' and form.validate() \
                and self._save(operators, pack, form.values):
            return HTTPFound(self._request.route_path(
                'pack_view', project_id=project['project_id'],
                pack_id=pack.pack_id))

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Pack'), replace=self._request.route_path(
                'pack_view', project_id=project['project_id'],
                pack_id=pack.pack_id))
        return {
            'age': age, 'form': form, 'tab_set': tab_set, 'action': action,
            'project': project, 'pack': pack, 'files': files,
            'file_type_labels': FILE_TYPE_LABELS, 'MIME_TYPES': MIME_TYPES,
            'operators': operators, 'events': self._paging_events(pack)[0]}

    # -------------------------------------------------------------------------
    def _settings_form(self, project, pack=None):
        """Return a pack settings form.

        :param project: (dictionary)
            Current project dictionary.
        :param pack: (:class:`~.models.pack.Pack` instance, optional)
            Current pack object.
        :return: (tuple)
            A tuple such as ``(form, tab_set, operators)``. ``operators`` is a
            list of tuples such as ``(user_id, user_name)``.
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='label',
            validator=Length(min=3, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=None))
        schema.add(SchemaNode(Boolean(), name='recursive', missing=False))
        schema.add(SchemaNode(String(), name='note', missing=None))
        defaults = {}
        operators = {}

        if pack is not None:
            # Files
            for item in pack.files:
                if item.file_type == 'template':
                    schema.add(SchemaNode(
                        String(), name='template_%s' % item.path,
                        validator=Length(max=PATH_LEN)))
                    defaults['template_%s' % item.path] = item.target
                name = '%s_%s_see' % (item.file_type, item.path)
                schema.add(SchemaNode(Boolean(), name=name, missing=False))
                defaults[name] = item.visible
            # Current task
            operators = operator_labels(project)
            schema.add(SchemaNode(
                Integer(), name='task_id', missing=None,
                validator=OneOf(project['task_labels'].keys())))
            schema.add(SchemaNode(
                String(), name='operator', missing=None,
                validator=OneOf([k[0] for k in operators])))
            defaults['task_id'] = pack.task_id
            defaults['operator'] = pack.operator_id and '%s%d' % (
                pack.operator_type, pack.operator_id) or None

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=pack),
            TabSet(self._request, PACK_SETTINGS_TABS), operators)

    # -------------------------------------------------------------------------
    def _save(self, operators, pack, values):
        """Save pack settings.

        :param operators: (list)
            List of operators.
        :param pack: (:class:`~..models.packs.Pack` instance)
            Pack to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        pack.label = normalize_spaces(values['label'], LABEL_LEN)
        pack.description = normalize_spaces(
            values['description'], DESCRIPTION_LEN)
        pack.recursive = values['recursive']
        pack.note = values['note'] and values['note'].strip() or None

        # Files
        for item in pack.files:
            item.visible = values[
                '%s_%s_see' % (item.file_type, item.path)]
            if item.file_type == 'template':
                item.target = values['template_%s' % item.path]
        if 'task' in self._request.session and \
                self._request.session['task']['pack_id'] == pack.pack_id:
            self._request.session['task']['files'] = file_details(
                self._request, pack)

        # Task
        old_task = pack.task_id
        old_operator = '%s%s' % (pack.operator_type, pack.operator_id)
        if values['task_id']:
            pack.task_id = values['task_id']
            task = DBSession.query(Task).filter_by(
                project_id=pack.project_id, task_id=pack.task_id).first()
            if task.operator_type == 'auto':
                pack.operator_type = 'auto'
                pack.operator_id = None
            elif values['operator']:
                pack.operator_type = values['operator'][0:4]
                pack.operator_id = int(values['operator'][4:])
            else:
                pack.operator_type = task.operator_type
                pack.operator_id = task.operator_id
        else:
            task = None
            pack.task_id = None
            pack.operator_type = None
            pack.operator_id = None
        DBSession.commit()

        # If new task
        if pack.task_id != old_task or '%s%s' \
                % (pack.operator_type, pack.operator_id) != old_operator:
            operator = dict(operators).get(
                '%s%s' % (pack.operator_type, str(pack.operator_id))) \
                or (task is None and self._request.session['name']) \
                or _('Automatic')
            operator = get_localizer(self._request).translate(operator)
            DBSession.add(PackEvent(
                pack.project_id, pack.pack_id, pack.task_id,
                task and task.label or '', pack.operator_type,
                pack.operator_id, '%s *' % operator))
            DBSession.commit()
            if task and task.operator_type == 'auto':
                task_auto_build(self._request, pack, task)

        return True

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``packs`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return: (:class:`~.models.packs.Pack` instance)
        """
        # Check unicity and create pack
        label = normalize_spaces(values['label'], LABEL_LEN)
        if DBSession.query(Pack) \
                .filter_by(project_id=project_id, label=label).first():
            self._request.session.flash(
                _('This pack already exists.'), 'alert')
            return

        # Create record
        pack = Pack(project_id, label, values['description'])
        DBSession.add(pack)
        DBSession.commit()

        return pack

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
        query = DBSession.query(Pack).filter_by(project_id=project_id)
        if 'f_label' in params:
            query = query.filter(
                Pack.label.ilike('%%%s%%' % params['f_label']))
        if 'f_task' in params and params['f_task'] != '*':
            query = query.filter(Pack.task_id == params['f_task'])

        # Order by
        oby = 'packs.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'packs', query), params

    # -------------------------------------------------------------------------
    def _current_pack(self, project_id, only_visible=True):
        """Return the current pack object.

        :param project_id: (string)
            Current project ID.
        :param only_visible: (boolean, default=True)
            If ``True``, it returns a list of only visible files otherwise it
            returns a dictionary.
        :return: (:class:`~.models.packs.Pack` instance,
            file_dictionary_or_list)

        ``request.session['container']`` is updated with ``pack_id`` and
        ``pack_label``.
        """
        # Pack
        pack_id = self._request.matchdict.get('pack_id')
        if pack_id is None:
            return None, file_details(self._request, None, only_visible)
        pack_id = int(pack_id)
        pack = DBSession.query(Pack).filter_by(
            project_id=project_id, pack_id=pack_id).first()
        if pack is None:
            raise HTTPNotFound(comment=_('This pack does not exist!'))

        # Container for storage
        self._request.session['container'] = {
            'project_id': project_id, 'pack_id': pack_id,
            'pack_label': pack.label}

        return pack, file_details(self._request, pack, only_visible)

    # -------------------------------------------------------------------------
    def _paging_events(self, pack):
        """Return a :class:`~..lib.renderer.Paging` object filled with events
        for pack ``pack_id`` of project ``project_id``.

        :param pack: (:class:`~..models.packs.Pack` instance)
            Current pack.
        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.renderer.Paging` object and ``filters`` a
            dictionary of filters.
        """
        # Parameters
        params = Paging.params(self._request, 'events', '-begin')

        # Query
        query = DBSession.query(PackEvent).filter_by(
            project_id=pack.project_id, pack_id=pack.pack_id)

        # Order by
        oby = 'packs_events.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'events', query), params
