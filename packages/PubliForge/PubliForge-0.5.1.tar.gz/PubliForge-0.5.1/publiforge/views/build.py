# $Id: build.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
# pylint: disable = I0011, C0322
"""Build view callables."""

from datetime import datetime, timedelta
from time import time
from os.path import join
from lxml import etree
from colander import SchemaNode, String, Length
import re

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.i18n import get_localizer

from ..lib.utils import _, normalize_name
from ..lib.xml import XML_NS, PUBLIFORGE_RNG_VERSION
from ..lib.views import get_action, current_storage, vcs_user, current_project
from ..lib.views import current_processing, variable_schema, describe_var
from ..lib.form import Form
from ..models import PATH_LEN, DBSession, close_dbsession
from ..models.projects import Project, ProjectPack


# =============================================================================
class BuildView(object):
    """Class to manage builds."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='build_launch',
                 renderer='../Templates/bld_launch.pt')
    def launch(self):
        """Launch one or more builds."""
        # Processing
        project = current_project(self._request)
        processing, processor = current_processing(self._request)
        output = processing.output and current_storage(
            self._request, processing.output.partition('/')[0])[0] or None

        # Packs
        pack_ids = self._request.matchdict.get('pack_ids').split('_')
        packs = DBSession.query(ProjectPack)\
                .filter_by(project_id=project['project_id'])\
                .filter(ProjectPack.pack_id.in_(pack_ids)).all()
        if packs is None:
            raise HTTPNotFound(comment=_('No pack to build!'))

        # Form, action & visible variables with help
        form, groups, variables = self._build_form(processing, processor)
        action, description = self._action(
            form, processing, processor, variables)

        # Launch builds
        build_ids = self._launch_builds(form, processing, processor, packs)
        if len(build_ids) == 1:
            self._request.breadcrumbs.pop()
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build_ids[0]))
        elif len(build_ids) > 1:
            self._request.breadcrumbs.pop()
            return HTTPFound(self._request.route_path(
                'project_results', project_id=project['project_id']))

        self._request.breadcrumbs.add(_('Build'))
        return {
            'form': form, 'action': action, 'project': project,
            'processing': processing, 'processor': processor, 'groups': groups,
            'variables': variables, 'description': description, 'packs': packs,
            'output': output}

    # -------------------------------------------------------------------------
    @view_config(route_name='build_view',
                 renderer='../Templates/bld_view.pt')
    def view(self):
        """Display a build, eventually, with its result."""
        # Build and project
        build, processing, processor, pack = self._current_build(True)
        project = current_project(
            self._request, int(build['build_id'].split('-')[0]))

        # Working?
        log = self._request.registry['fbuild'].progress(
            self._request, (build['build_id'],))[0]
        if log:
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build['build_id']))

        # Form & visible variables
        form, groups, variables = self._build_form(processing, processor)

        # Action
        action, description = self._action(
            form, processing, processor, variables)
        if action == 'exp!':
            return self._export_build(project, processing, processor, pack)

        # Launch build
        build_ids = self._launch_builds(form, processing, processor, (pack,))
        if build_ids:
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build_ids[0]))

        # Result
        result = self._request.registry['fbuild']\
                 .result(self._request, build['build_id'])
        log = '\n'.join([
            '%s [%-7s] %s' % (
                datetime.fromtimestamp(k[0]).isoformat(' ').split('.')[0],
                k[1], k[3]) for k in result.get('log', [])])

        self._request.breadcrumbs.add(
            _('Build'), replace=self._request.route_path(
            'build_progress', build_id=build['build_id']))
        return {
            'form': form, 'action': action, 'project': project,
            'processing': processing, 'processor': processor, 'groups': groups,
            'variables': variables, 'description': description, 'pack': pack,
            'output': build['output'], 'build': build, 'result': result,
            'message': result.get('message'), 'log': log}

    # -------------------------------------------------------------------------
    @view_config(route_name='build_progress',
                 renderer='../Templates/bld_progress.pt')
    def progress(self):
        """Display the build progress."""
        # Stop?
        build = self._current_build()[0]
        registry = self._request.registry
        is_owner = registry['fbuild'].is_owner(
            self._request, build['build_id'])
        if 'stp!' in self._request.params and is_owner:
            registry['fbuild'].stop(self._request, build['build_id'])

        # Working?
        working, prgrss = \
            registry['fbuild'].progress(self._request, (build['build_id'],))
        if not working:
            return HTTPFound(self._request.route_path(
                'build_view', build_id=build['build_id'], _anchor='build'))
        playing = str(
            timedelta(seconds=time() - prgrss[build['build_id']][3]))\
            .split('.')[0]

        # Project
        project = current_project(
            self._request, int(build['build_id'].partition('-')[0]))

        # Refresh
        if not 'ajax' in self._request.params \
               and not 'stp?' in self._request.params:
            self._request.response.headerlist.append((
                'Refresh', registry.settings.get('refresh.short', '3')))

        self._request.breadcrumbs.add(_('On progress...'))
        return {
            'form': Form(self._request), 'project': project, 'build': build,
            'is_owner': is_owner, 'progress': prgrss[build['build_id']],
            'playing': playing}

    # -------------------------------------------------------------------------
    @view_config(route_name='build_progress_ajax', renderer='json')
    def progress_ajax(self):
        """Return a JSON response for the build progress for AJAX request."""
        build_id = self._request.matchdict['build_id']
        working, prgrss = self._request.registry['fbuild']\
            .progress(self._request, (build_id,))
        playing = working and \
            str(timedelta(seconds=time() - prgrss[build_id][3])).split('.')[0]\
            or ''
        return {
            'working': working, 'percent': prgrss[build_id][1],
            'message': prgrss[build_id][2], 'playing': playing}

    # -------------------------------------------------------------------------
    @view_config(route_name='build_complete',
                 permission=NO_PERMISSION_REQUIRED)
    def complete(self):
        """Complete a build."""
        build_id = self._request.matchdict['build_id']
        key = self._request.matchdict['key']

        made = self._request.registry['fbuild']\
               .complete(self._request, build_id, key)
        return Response(made and '' or 'Unable to complete "%s"' % build_id)

    # -------------------------------------------------------------------------
    @view_config(route_name='build_log')
    def log(self):
        """Download current log."""
        build = self._current_build()[0]
        project = current_project(
            self._request, int(build['build_id'].partition('-')[0]))
        content = self._request.registry['fbuild']\
                  .result(self._request, build['build_id'])
        content = '\n'.join([
            '%s [%-7s] %s' % (
                datetime.fromtimestamp(k[0]).isoformat(' ').split('.')[0],
                k[1], k[3]) for k in content.get('log', [])])
        filename = normalize_name('%s-%s.log' % (
            project['label'], build['build_id'].partition('-')[2]))
        response = Response(content, content_type='text/plain')
        response.headerlist.append(('Content-Disposition',
            'attachment; filename="%s"' % filename))
        return response

    # -------------------------------------------------------------------------
    def _current_build(self, full=False):
        """Initialize ``request.session['build']`` and return it as current
        build dictionary.

        If ``full`` is ``True``, this method also returns
        :class:`~.models.projects.ProjectProcessing` object, processor
        :class:`lxml.etree.ElementTree` object and
        :class:`~.models.projects.ProjectPack` object.

        :param full: (boolean)
            If ``True``, force database reading and return processing and
            pack objects.
        :return: (tuple)
            A tuple such as ``(build_dictionary, processing_object,
            pack_object)`` or a :class:`pyramid.httpexceptions.`HTTPNotFound`
            exception.

        ``build_dictionary`` has the following keys: ``build_id``,
        ``processing_id``, ``processing_label``, ``varaiable_count``,
        ``pack_id``, ``pack_label``, ``file_count``, ``output``.
        """
        # Already in session
        build_id = self._request.matchdict['build_id']
        if not full and 'build' in self._request.session \
               and self._request.session['build']['build_id'] == build_id:
            return self._request.session['build'], None, None, None

        # Processing & processor
        project_id, processing_id, pack_id = build_id.split('-')
        processing, processor = \
            current_processing(self._request, project_id, processing_id)

        # Pack
        pack = DBSession.query(ProjectPack).filter_by(
            project_id=project_id, pack_id=pack_id).first()
        if pack is None:
            raise HTTPNotFound(comment=_('This pack does not exist!'))
        file_count = len([k for k in pack.files if k.file_type == 'file'])

        # Output
        output = processing.output and current_storage(
            self._request, processing.output.partition('/')[0])[0] or None
        if output:
            output = {
                'storage_id': output['storage_id'], 'label': output['label'],
                'path': processing.output.partition('/')[2]}

        self._request.session['build'] = {
            'build_id': build_id, 'processing_id': processing_id,
            'processing_label': processing.label,
            'variable_count': len(processing.variables), 'pack_id': pack_id,
            'pack_label': pack.label, 'file_count': file_count,
            'output': output}
        return self._request.session['build'], processing, processor, pack

    # -------------------------------------------------------------------------
    def _build_form(self, processing, processor):
        """Return a build form with a validating schema for visible variables.

        :param processing:
            (:class:`~.models.projects.ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (tuple)
            A tuple such as ``(form, groups, variables)``

        ``groups`` is a list of group :class:`lxml.etree.Element` objects
        containing visible variables. ``variables`` is a dictionary of
        :class:`~.models.projects.ProjectProcessingVariable` objects of visible
        variables.
        """
        variables = dict([
            (k.name, k) for k in processing.variables if k.visible])
        groups = []
        for group in processor.findall('processor/variables/group'):
            for var in group.findall('var'):
                if var.get('name') in variables:
                    groups.append(group)
                    break

        schema, defaults = variable_schema(processor, variables, True, False)
        schema.add(SchemaNode(String(), name='path',
            validator=Length(max=PATH_LEN), missing=None))
        defaults['path'] = processing.output.partition('/')[2]
        form = Form(
            self._request, schema=schema, defaults=defaults, obj=processing)
        return form, groups, variables

    # -------------------------------------------------------------------------
    def _launch_builds(self, form, processing, processor, packs):
        """Launch build.

        :param form: (:class:`~.lib.form.Form` instance)
             Build form.
        :param processing:
             (:class:`~.models.projects.ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param packs: (list)
             List of :class:`~.models.projects.ProjectPack` objects.
        :return: (list)
             List of launched build
        """
        if not 'bld!.x' in self._request.params \
               or not form.validate(obj=processing):
            return tuple()
        processing.output = processing.output.partition('/')[0] \
            + '/' + (form.values['path'] or '')

        # Save variable modifications
        for var in processing.variables:
            if var.visible:
                var.value = form.values[var.name]
        DBSession.commit()

        # Create builds and start them
        build_ids = []
        for pack in packs:
            front_build = self._request.registry['fbuild'].start_build(
                self._request, processing, processor, pack)
            if front_build is not None \
                   and not self._request.session.peek_flash('alert'):
                build_ids.append(front_build.uid)

        return build_ids

    # -------------------------------------------------------------------------
    def _action(self, form, processing, processor, variables):
        """Return current action and a description text.

        :param form: (:class:`~.lib.form.Form` instance)
            Current form.
        :param processing:
             (:class:`~.models.projects.ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
            Variables of current processing.
        :return: (tuple)
            A tuple such as ``(action, description)``.
        """
        description = None
        action = get_action(self._request)[0]

        if action[0:4] == 'des!':
            description = describe_var(
                self._request, processor, variables, action[4:])
        elif action[0:4] == 'rst!':
            name = action[4:]
            if name in variables:
                form.values[name] = variables[name].default
                form.static(name)
        elif action[0:4] == 'upl!':
            action = action[4:].split('/')
            self._file_upload(action[0], action[1:], processing.label)
            action = ''

        return action, description

    # -------------------------------------------------------------------------
    def _export_build(self, project, processing, processor, pack):
        """Export build.

        :param project: (dictionary)
            Project dictionary.
        :param processing:
            (:class:`~.models.projects.ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param pack: (:class:`~.models.projects.ProjectPack` instance)
        :return: (:class:`pyramid.response.Response` instance)
        """
        # Header
        settings = self._request.registry.settings
        root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)
        build_elt = etree.SubElement(root, 'build')
        build_elt.set('%sid' % XML_NS, '%s_%d-%d-%d' % (settings['uid'],
            project['project_id'], processing.processing_id, pack.pack_id))

        # Settings
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'settings')
        etree.SubElement(group_elt, 'setting', key='storage.root')\
            .text = '../../Storages~'
        etree.SubElement(group_elt, 'setting', key='build.root')\
            .text = '../../Builds~'
        etree.SubElement(group_elt, 'setting', key='build.develop')\
            .text = settings.get('build.develop', 'true')
        etree.SubElement(group_elt, 'setting', key='processor.roots')\
            .text = '../../Processors'

        # Processing
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'processing')
        etree.SubElement(group_elt, 'processor').text = processing.processor
        Project.xml_variables(group_elt, processing, processor, False)
        Project.xml_file_set(group_elt, processing, 'resource')
        Project.xml_file_set(group_elt, processing, 'template')

        # Pack
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'pack')
        if pack.recursive:
            group_elt.set('recursive', 'true')
        Project.xml_file_set(group_elt, pack, 'file')
        Project.xml_file_set(group_elt, pack, 'resource')
        Project.xml_file_set(group_elt, pack, 'template')

        # Response
        filename = normalize_name('%s-%d-%d.pfb.xml' % (
            project['label'], processing.processing_id, pack.pack_id))
        xml = etree.tostring(
            root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        xml = re.sub('\s*<(/?)value>\s*', '<\\1value>', xml)
        response = Response(xml, content_type='application/xml')
        response.headerlist.append(('Content-Disposition',
                'attachment; filename="%s"' % filename))
        return response

    # -------------------------------------------------------------------------
    def _file_upload(self, storage_id, path, processing_label):
        """Update a file in a storage.

        :param storage_id: (string)
            Storage ID.
        :param path: (list)
            Splitted relative path of the file to update.
        :param processing_label: (string)
            Processing label.
        """
        upload_file = self._request.params.get('upload_file')
        if upload_file is None or isinstance(upload_file, basestring)\
               or not path:
            return

        storage, handler = current_storage(self._request, storage_id)
        if storage['perm'] == 'user':
            self._request.session.flash(_(
                "You can't modify this storage!"), 'alert')
            return
        if path[-1] != upload_file.filename:
            self._request.session.flash(
                _('File names are different.'), 'alert')
            return

        message = get_localizer(self._request).translate(
            _('Updated for "${p}"', {'p': processing_label}))
        handler.upload(vcs_user(
            self._request, storage), join('.', *path[0:-1]),
            upload_file, path[-1], message)
        if handler.progress()[0] == 'error':
            self._request.session.flash(handler.progress()[1], 'alert')
        else:
            self._request.session.flash(_('File has been updated.'))
