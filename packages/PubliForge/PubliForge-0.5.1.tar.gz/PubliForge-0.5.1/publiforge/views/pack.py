# $Id: pack.py e8da66c6d933 2012/02/18 22:34:11 patrick $
# pylint: disable = I0011, C0322
"""Pack view callables."""

from colander import Mapping, SchemaNode, String, Boolean, Length

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ..lib.utils import _, FILE_TYPES
from ..lib.views import get_action, current_project, file_infos
from ..lib.form import Form
from ..lib.renderer import TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.projects import ProjectPack, ProjectPackFile


PACK_SETTINGS_TABS = (_('Description'), _('Files'))
FILE_TYPE_LABELS = {'file': _('Files to process'),
    'resource': _('Resource files'), 'template': _('Template files')}


# =============================================================================
class PackView(object):
    """Class to manage packs."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_view',
                 renderer='../Templates/pck_view.pt')
    def view(self):
        """Display a pack."""
        project = current_project(self._request)
        pack = self._current_pack(project)
        tab_set = TabSet(self._request, PACK_SETTINGS_TABS)
        form = Form(self._request,
                    defaults={'processing_id': project['processing_id']})

        # Action
        if get_action(self._request)[0] == 'bld!' and form.validate():
            return HTTPFound(self._request.route_path(
                'build_launch', project_id=project['project_id'],
                processing_id=form.values['processing_id'],
                pack_ids=pack.pack_id))

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Pack'), replace=self._request.route_path('pack_edit',
            project_id=project['project_id'], pack_id=pack.pack_id))

        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'pack': pack,
            'files': file_infos(self._request, pack),
            'file_type_labels': FILE_TYPE_LABELS, 'FILE_TYPES': FILE_TYPES}

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_create', renderer='../Templates/pck_edit.pt')
    def create(self):
        """Create a pack."""
        project = current_project(self._request)
        form, tab_set = self._settings_form()

        if form.validate():
            pack = self._create(project['project_id'], form.values)
            if pack is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path('pack_edit',
                    project_id=pack.project_id, pack_id=pack.pack_id,
                    _anchor='tab1'))

        self._request.breadcrumbs.add(_('Pack creation'))
        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'pack': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='pack_edit', renderer='../Templates/pck_edit.pt')
    def edit(self):
        """Edit a pack."""
        # Environment
        project = current_project(self._request)
        pack = self._current_pack(project)
        form, tab_set = self._settings_form(pack)

        # Action
        # pylint: disable = I0011, E1103
        action = get_action(self._request)[0]
        if action[0:4] == 'rmv!':
            DBSession.query(ProjectPackFile).filter_by(
                project_id=project['project_id'], pack_id=pack.pack_id,
                file_type=action[4:].partition('_')[0],
                path=action[4:].partition('_')[2]).delete()
            DBSession.commit()
        elif action == 'sav!' and form.validate(pack):
            for item in pack.files:
                item.visible = form.values[
                    '%s_%s_see' % (item.file_type, item.path)]
                if item.file_type == 'template':
                    item.target = form.values['template_%s' % item.path]
            DBSession.commit()
            return HTTPFound(self._request.route_path('pack_view',
                project_id=project['project_id'], pack_id=pack.pack_id))

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Pack'), replace=self._request.route_path('pack_view',
            project_id=project['project_id'], pack_id=pack.pack_id))
        return {
            'form': form, 'tab_set': tab_set, 'action': action,
            'project': project, 'pack': pack,
            'files': file_infos(self._request, pack),
            'file_type_labels': FILE_TYPE_LABELS, 'FILE_TYPES': FILE_TYPES}

    # -------------------------------------------------------------------------
    def _current_pack(self, project):
        """Return the current pack object.

        :param project: (dictionary)
            Current project dictionary
        :return: (:class:`~.models.projects.ProjectPack` instance)

        ``request.session['container']`` is updated with ``pack_id`` and
        ``pack_label``.
        """
        project_id = project['project_id']
        pack_id = int(self._request.matchdict.get('pack_id'))

        # Pack
        pack = DBSession.query(ProjectPack).filter_by(
            project_id=project_id, pack_id=pack_id).first()
        if pack is None:
            raise HTTPNotFound(comment=_('This pack does not exist!'))

        # Container for storage
        self._request.session['container'] = {'project_id': project_id,
            'pack_id': pack_id, 'pack_label': pack.label}

        return pack

    # -------------------------------------------------------------------------
    def _settings_form(self, pack=None):
        """Return a pack settings form.

        :param pack: (:class:`~.models.projects.ProjectPack`
            instance, optional) Current pack object.
        :return: (tuple)
             A tuple such as ``(form, tab_set)``
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=3, max=LABEL_LEN)))
        schema.add(SchemaNode(String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=None))
        schema.add(SchemaNode(Boolean(), name='recursive', missing=False))
        defaults = {}

        if pack is not None:
            for item in pack.files:
                if item.file_type == 'template':
                    schema.add(SchemaNode(
                        String(), name='template_%s' % item.path,
                        validator=Length(max=PATH_LEN)))
                    defaults['template_%s' % item.path] = item.target
                name = '%s_%s_see' % (item.file_type, item.path)
                schema.add(SchemaNode(Boolean(), name=name, missing=False))
                defaults[name] = item.visible

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=pack),
            TabSet(self._request, PACK_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``projects_packs`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return:
            (:class:`~.models.projects.ProjectPack`  instance)
        """
        # Check unicity and create pack
        label = ' '.join(values['label'].split()).strip()
        if DBSession.query(ProjectPack) \
               .filter_by(project_id=project_id, label=label).first():
            self._request.session.flash(
                _('This pack already exists.'), 'alert')
            return

        # Create record
        pack = ProjectPack(project_id, label, values['description'])
        DBSession.add(pack)
        DBSession.commit()

        return pack
