# $Id: processing.py 76f5e2815793 2012/08/04 21:23:42 patrick $
# pylint: disable = I0011, C0322
"""Processing view callables."""

from os.path import join, normpath
from colander import Mapping, SchemaNode
from colander import String, Length, OneOf
from webhelpers.html import literal

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ..lib.utils import _, MIME_TYPES, has_permission, normalize_spaces
from ..lib.xml import export_configuration, local_text
from ..lib.form import Form
from ..lib.views import get_action, current_project
from ..lib.views import current_processing, file_details
from ..lib.views import variable_schema, variable_description
from ..lib.renderer import TabSet
from ..views.pack import FILE_TYPE_LABELS
from ..models import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.processors import Processor
from ..models.processings import ADD2PACK_TARGETS
from ..models.processings import Processing, ProcessingFile, ProcessingVariable


PROCESSING_SETTINGS_TABS = (
    _('Description'), _('Variables'), _('Files'), _('Output'))


# =============================================================================
class ProcessingView(object):
    """Class to manage processings."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='processing_view', renderer='../Templates/prc_view.pt')
    def view(self):
        """Display processing settings."""
        # Permission
        project = current_project(self._request)
        i_editor = project['perm'] == 'leader' \
            or has_permission(self._request, 'prj_editor')

        # Environment
        processing, processor, output = current_processing(
            self._request, container=True)
        variables = self._variable_defaults(processor, processing.variables)
        tab_set = TabSet(self._request, PROCESSING_SETTINGS_TABS)

        # Action
        action, description = self._action(
            None, processing, processor, variables, i_editor)
        if action == 'exp!':
            if not processing.processor.startswith('Parallel'):
                return export_configuration((processing.xml(processor),))
            self._request.session.flash(_(
                'You cannot export this processing.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Processing'), replace=self._request.route_path(
                'processing_edit', project_id=project['project_id'],
                processing_id=processing.processing_id))

        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'project': project, 'processing': processing,
            'processor': processor, 'variables': variables,
            'files': file_details(self._request, processing, False),
            'file_type_labels': FILE_TYPE_LABELS, 'MIME_TYPES': MIME_TYPES,
            'output': output, 'ADD2PACK_TARGETS': ADD2PACK_TARGETS,
            'description': description, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='processing_create', renderer='../Templates/prc_edit.pt')
    def create(self):
        """Create a processing."""
        # Permission
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Environment
        processor_id = self._request.params.get('processor_id')
        processor_labels = Processor.labels(self._request)
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='processor_id',
            validator=OneOf(processor_labels.keys())))
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description', missing='',
            validator=Length(max=DESCRIPTION_LEN)))
        form = Form(self._request, schema=schema)
        tab_set = TabSet(self._request, PROCESSING_SETTINGS_TABS)

        # Action
        action = get_action(self._request)[0]
        description = None
        if action == 'des!' and processor_id:
            description = Processor.description(self._request, processor_id)
            description = literal(
                '<b>%s (%s)</b><br/>%s' %
                (processor_labels[processor_id], processor_id, description))
        elif action == 'sav!' and form.validate():
            processing = self._create(project['project_id'], form.values)
            if processing is not None:
                if 'project' in self._request.session:
                    del self._request.session['project']
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'processing_edit', project_id=processing.project_id,
                    processing_id=processing.processing_id))

        self._request.breadcrumbs.add(_('Processing creation'))
        return {
            'form': form, 'tab_set': tab_set, 'project': project,
            'processing': None, 'processor_labels': processor_labels,
            'description': description}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='processing_edit', renderer='../Templates/prc_edit.pt')
    def edit(self):
        """Edit a processing."""
        # Permission
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Environment
        processing, processor, output = current_processing(
            self._request, container=True)
        variables = self._variable_defaults(processor, processing.variables)
        form, tab_set = self._settings_form(processing, processor, variables)

        # Action
        action, description = self._action(
            form, processing, processor, variables, True)
        view_path = self._request.route_path(
            'processing_view', project_id=processing.project_id,
            processing_id=processing.processing_id)
        if action == 'view':
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Processing'), replace=view_path)

        return {
            'form': form, 'tab_set': tab_set, 'action': action,
            'file_type_labels': FILE_TYPE_LABELS, 'MIME_TYPES': MIME_TYPES,
            'project': project, 'processing': processing,
            'processor': processor, 'variables': variables,
            'files': file_details(self._request, processing, False),
            'output': output, 'ADD2PACK_TARGETS': ADD2PACK_TARGETS,
            'description': description}

    # -------------------------------------------------------------------------
    def _settings_form(self, processing, processor, variables):
        """Return a processing settings form.

        :param processing: (:class:`~..models.processings.Processing` instance)
            Current processing object.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
            Variables of current processing.
        :return: (tuple)
             A tuple such as ``(form, tab_set)``
        """
        schema, defaults = variable_schema(processor, variables)
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        defaults['label'] = processing.label
        defaults['description'] = processing.description

        if not processing.output \
                and processor.findtext('processor/output') is not None:
            processing.output = processor.findtext('processor/output').strip()
            processing.add2pack = \
                processor.find('processor/output').get('add2pack')
            DBSession.commit()
        if processing.output:
            schema.add(SchemaNode(
                String(), name='output',
                validator=Length(max=PATH_LEN), missing=''))
            schema.add(SchemaNode(
                String(), name='add2pack',
                validator=OneOf(ADD2PACK_TARGETS.keys()), missing=None))
            defaults['output'] = processing.output.partition('/')[2]
            defaults['add2pack'] = processing.add2pack

        for item in processing.files:
            if item.file_type == 'template':
                schema.add(SchemaNode(
                    String(), name='template_%s' % item.path,
                    validator=Length(max=PATH_LEN)))
                defaults['template_%s' % item.path] = item.target

        return (Form(self._request, schema=schema, defaults=defaults),
                TabSet(self._request, PROCESSING_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _action(self, form, processing, processor, variables,
                show_processor_defaults=False):
        """Return current action and help message.

        :param form: (:class:`~..lib.form.Form` instance)
            Current form.
        :param processing:
            (:class:`~..models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
            Variables of current processing.
        :param show_processor_defaults: (boolean, default=False)
            Show the processor default value if any.
        :return: (tuple)
            A tuple such as ``(action, description)``.
        """
        action = get_action(self._request)[0]
        description = None

        if action == 'des!':
            description = Processor.description(self._request, xml=processor)
            description = literal('<b>%s </b><br/>%s' % (local_text(
                processor, 'processor/label', self._request), description))
        elif action[0:4] == 'des!':
            description = variable_description(
                self._request, processor, variables, action[4:],
                show_processor_defaults)
        elif action[0:4] == 'rst!':
            name = action[4:]
            var = processor.xpath(
                'processor/variables/group/var[@name="%s"]' % name)
            if len(var) == 1 and var[0].findtext('default') is not None:
                value = var[0].findtext('default').strip()
                form.values[name] = value == 'true' \
                    if var[0].get('type') == 'boolean' else value
                form.values['%s_def' % name] = form.values[name]
                form.static(name)
                form.static('%s_def' % name)
        elif action[0:4] == 'rmv!':
            DBSession.query(ProcessingFile).filter_by(
                project_id=processing.project_id,
                processing_id=processing.processing_id,
                file_type=action[4:].partition('_')[0],
                path=action[4:].partition('_')[2]).delete()
            DBSession.commit()
        elif action == 'sav!' and form.validate() \
                and self._save(processing, processor, form.values):
            action = 'view'

        return action, description

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``projects_processings`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return:
            (:class:`~..models.processings.Processing` instance)
        """
        # Check unicity and create processing
        label = normalize_spaces(values['label'], LABEL_LEN)
        processing = DBSession.query(Processing).filter_by(
            project_id=project_id, label=label).first()
        if processing is not None:
            self._request.session.flash(
                _('This processing already exists.'), 'alert')
            return
        processing = Processing(
            project_id, label, values['description'], values['processor_id'])

        # Create variables
        processor = self._request.registry['fbuild'].processor(
            self._request, values['processor_id'])
        for var in processor.findall('processor/variables/group/var'):
            if var.findtext('default') is not None:
                value = var.findtext('default').strip()
                processing.variables.append(
                    ProcessingVariable(var.get('name'), value, value))

        # Create output
        if processor.findtext('processor/output') is not None:
            processing.output = processor.findtext('processor/output').strip()
            processing.add2pack = \
                processor.find('processor/output').get('add2pack')

        DBSession.add(processing)
        DBSession.commit()

        return processing

    # -------------------------------------------------------------------------
    def _save(self, processing, processor, values):
        """Save a processing settings.

        :param processing: (:class:`~..models.processings.Processing` instance)
            Processing to update.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        processing.label = normalize_spaces(values['label'], LABEL_LEN)
        processing.description = normalize_spaces(
            values['description'], DESCRIPTION_LEN)

        if processing.output:
            processing.output = normpath(join(
                processing.output.partition('/')[0],
                values['output'].replace('..', '')))
            processing.add2pack = values['add2pack']

        DBSession.query(ProcessingVariable).filter_by(
            project_id=processing.project_id,
            processing_id=processing.processing_id).delete()
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            default = var.findtext('default', '').strip()
            if var.get('type') == 'integer':
                default = int(default or '0')
            elif var.get('type') == 'boolean':
                default = (default == 'true')
            if values.get(name) != default \
                    or values.get('%s_see' % name) != bool(var.get('visible')):
                processing.variables.append(ProcessingVariable(
                    name,
                    values.get(name) if values.get(name) != default else None,
                    values.get('%s_see' % name)
                    if values.get('%s_see' % name) != bool(var.get('visible'))
                    else None))

        for item in processing.files:
            if item.file_type == 'template':
                item.target = values['template_%s' % item.path]

        DBSession.commit()
        del self._request.session['project']
        if 'build' in self._request.session:
            del self._request.session['build']

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _variable_defaults(cls, processor, variables):
        """Return a dictionary of variable default values.

        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (:class:`~.models.processings.ProcessingVariable`)
            Variables of current processing.
        :return: (dictionay)
            A dictionary such as {<name>: (<default>, <visible>, <label>),...}.
        """
        variables = dict([(k.name, k) for k in variables])
        defaults = {}
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            default = variables[name].default if name in variables \
                and variables[name].default is not None \
                else var.findtext('default')
            visible = variables[name].visible if name in variables \
                and variables[name].visible is not None \
                else bool(var.get('visible'))
            label = None
            if default is not None and var.get('type') == 'select':
                label = dict([
                    (k.get('value', k.text), k.text)
                    for k in var.findall('option')])[default]
            defaults[name] = (default, visible, label)
        return defaults
