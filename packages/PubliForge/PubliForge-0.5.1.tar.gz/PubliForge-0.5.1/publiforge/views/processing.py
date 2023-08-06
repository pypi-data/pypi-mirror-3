# $Id: processing.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
# pylint: disable = I0011, C0322
"""Processing view callables."""

from os.path import join, normpath
from colander import Mapping, SchemaNode
from colander import String, Length, OneOf
from webhelpers.html import literal

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ..lib.utils import _, FILE_TYPES, has_permission
from ..lib.xml import export_configuration, local_text
from ..lib.form import Form
from ..lib.views import get_action, current_storage, current_project
from ..lib.views import current_processing, file_infos, variable_schema
from ..lib.views import describe_var
from ..lib.renderer import TabSet
from ..views.pack import FILE_TYPE_LABELS, file_infos
from ..models import LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.processors import Processor
from ..models.projects import ProjectProcessing, ProjectProcessingFile
from ..models.projects import ProjectProcessingVariable


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
    @view_config(route_name='processing_view',
                 renderer='../Templates/prc_view.pt')
    def view(self):
        """Display processing settings."""
        # Permission
        project = current_project(self._request)
        i_editor = has_permission(self._request, 'prj_editor') \
            or project['perm'] == 'editor'

        # Environment
        processing, processor = current_processing(
            self._request, container=True)
        variables = dict([(k.name, k) for k in processing.variables])
        tab_set = TabSet(self._request, PROCESSING_SETTINGS_TABS)
        output = processing.output and current_storage(
            self._request, processing.output.partition('/')[0])[0] or None

        # Action
        action, description = self._action(
            None, processing, processor, variables)
        if action == 'exp!':
            return  export_configuration((processing.xml(processor),))

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Processing'), replace=self._request.route_path(
            'processing_edit', project_id=project['project_id'],
            processing_id=processing.processing_id))

        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'file_type_labels': FILE_TYPE_LABELS, 'FILE_TYPES': FILE_TYPES,
            'project': project, 'processing': processing,
            'processor': processor, 'variables': variables,
            'files': file_infos(self._request, processing), 'output': output,
            'description': description, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(route_name='processing_create',
                 renderer='../Templates/prc_edit.pt')
    def create(self):
        """Create a processing."""
        # Permission
        project = current_project(self._request)
        if not has_permission(self._request, 'prj_editor') \
               and project['perm'] != 'editor':
            raise HTTPForbidden()

        # Environment
        processor_id = self._request.params.get('processor_id')
        processor_labels = Processor.labels(self._request)
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(String(), name='description', missing='',
            validator=Length(max=DESCRIPTION_LEN)))
        schema.add(SchemaNode(String(), name='processor_id',
            validator=OneOf(processor_labels.keys())))
        form = Form(self._request, schema=schema)
        tab_set = TabSet(self._request, PROCESSING_SETTINGS_TABS)

        # Action
        action = get_action(self._request)[0]
        description = None
        if action == 'des!' and processor_id:
            description = Processor.description(self._request, processor_id)
            description = literal('<b>%s (%s)</b><br/>%s' %
                (processor_labels[processor_id], processor_id, description))
        elif action == 'sav!' and form.validate():
            processing = self._create(project['project_id'], form.values)
            if processing is not None:
                if 'project' in self._request.session:
                    del self._request.session['project']
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path('processing_edit',
                    project_id=processing.project_id,
                    processing_id=processing.processing_id))

        self._request.breadcrumbs.add(_('Processing creation'))
        return {
            'form': form, 'tab_set': tab_set, 'project': project,
            'processing': None, 'processor_labels': processor_labels,
            'description': description}

    # -------------------------------------------------------------------------
    @view_config(route_name='processing_edit',
                 renderer='../Templates/prc_edit.pt')
    def edit(self):
        """Edit a processing."""
        # Permission
        project = current_project(self._request)
        if not has_permission(self._request, 'prj_editor') \
               and project['perm'] != 'editor':
            raise HTTPForbidden()

        # Environment
        processing, processor = current_processing(
            self._request, container=True)
        variables = dict([(k.name, k) for k in processing.variables])
        form, tab_set = self._settings_form(processing, processor, variables)
        output = processing.output and current_storage(
            self._request, processing.output.partition('/')[0])[0] or None

        # Action
        action, description = self._action(
            form, processing, processor, variables, True)
        view_path = self._request.route_path('processing_view',
            project_id=processing.project_id,
            processing_id=processing.processing_id)
        if action == 'view':
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Processing'), replace=view_path)

        return {
            'form': form, 'tab_set': tab_set, 'action': action,
            'file_type_labels': FILE_TYPE_LABELS, 'FILE_TYPES': FILE_TYPES,
            'project': project, 'processing': processing,
            'processor': processor, 'variables': variables,
            'files': file_infos(self._request, processing), 'output': output,
            'description': description}

    # -------------------------------------------------------------------------
    def _settings_form(self, processing, processor, variables):
        """Return a processing settings form.

        :param processing: (:class:`~..models.projects.ProjectProcessing`
            instance) Current processing object.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
            Variables of current processing.
        :return: (tuple)
             A tuple such as ``(form, tab_set)``
        """
        schema, defaults = variable_schema(processor, variables)
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        defaults['label'] = processing.label
        defaults['description'] = processing and processing.description

        if not processing.output \
               and processor.findtext('processor/output') is not None:
            processing.output = processor.findtext('processor/output').strip()
            DBSession.commit()
        if processing.output:
            schema.add(SchemaNode(String(), name='output',
                validator=Length(max=PATH_LEN), missing=''))
            defaults['output'] = processing.output.partition('/')[2]

        for item in processing.files:
            if item.file_type == 'template':
                schema.add(SchemaNode(String(), name='template_%s' % item.path,
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
            (:class:`~..models.projects.ProjectProcessing` instance)
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
            description = describe_var(self._request, processor, variables,
                action[4:], show_processor_defaults)
        elif action[0:4] == 'rst!':
            name = action[4:]
            var = processor.xpath(
                'processor/variables/group/var[@name="%s"]' % name)
            if len(var) == 1 and var[0].findtext('default') is not None:
                value = var[0].findtext('default').strip()
                form.values[name] = value
                form.static(name)
                form.values['%s_def' % name] = value
                form.static('%s_def' % name)
        elif action[0:4] == 'rmv!':
            DBSession.query(ProjectProcessingFile).filter_by(
                project_id=processing.project_id,
                processing_id=processing.processing_id,
                file_type=action[4:].partition('_')[0],
                path=action[4:].partition('_')[2]).delete()
            DBSession.commit()
        elif action == 'sav!' and form.validate() \
                 and self._save(processing, processor, variables, form.values):
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
            (:class:`~..models.projects.ProjectProcessing`  instance)
        """
        # Check unicity and create processing
        label = u' '.join(values['label'].split())
        processing = DBSession.query(ProjectProcessing).filter_by(
            project_id=project_id, label=label).first()
        if processing is not None:
            self._request.session.flash(
                _('This processing already exists.'), 'alert')
            return
        processing = ProjectProcessing(
            project_id, label, values['description'], values['processor_id'])

        # Create variables
        processor = self._request.registry['fbuild'].processor(
            self._request, values['processor_id'])
        if processor.findtext('processor/output') is not None:
            processing.output = processor.findtext('processor/output').strip()
        for var in processor.findall('processor/variables/group/var'):
            if var.findtext('default') is not None:
                value = var.findtext('default').strip()
                processing.variables.append(
                    ProjectProcessingVariable(var.get('name'), value, value))

        DBSession.add(processing)
        DBSession.commit()

        return processing

    # -------------------------------------------------------------------------
    def _save(self, processing, processor, variables, values):
        """Save a processing settings.

        :param processing:
            (:class:`~..models.projects.ProjectProcessing` instance) Processing
            to update.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
            Variables of current processing.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        processing.label = ' '.join(values['label'].split())
        processing.description = ' '.join(values['description'].split())

        if processing.output:
            processing.output = normpath(join(
                processing.output.partition('/')[0],
                values['output'].replace('..', '')))

        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            if name in variables:
                variables[name].value = values[name]
                variables[name].default = values['%s_def' % name]
                variables[name].visible = values['%s_see' % name]
            else:
                processing.variables.append(ProjectProcessingVariable(
                    name, values[name], values['%s_def' % name],
                    values['%s_see' % name]))

        for item in processing.files:
            if item.file_type == 'template':
                item.target = values['template_%s' % item.path]

        DBSession.commit()
        if 'build' in self._request.session:
            del self._request.session['build']

        return True
