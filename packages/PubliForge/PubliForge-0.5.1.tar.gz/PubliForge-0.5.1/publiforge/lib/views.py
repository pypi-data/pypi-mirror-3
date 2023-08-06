# $Id: views.py ada86c3ea608 2012/03/22 22:52:47 patrick $
"""Some various utilities for views."""

from os import walk
from os.path import exists, join, isfile, dirname, relpath, basename, normpath
import zipfile
import tempfile
from sqlalchemy import select, desc
from colander import SchemaNode, Mapping, String, Integer, Boolean
from colander import All, Length, Regex, OneOf
from webhelpers.html import literal

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.i18n import get_localizer
from pyramid.response import Response

from .utils import _, EXCLUDED_FILES, decrypt, get_mime_type, has_permission
from .xml import local_text
from .renderer import Paging
from .form import grid_item
from ..models import VALUE_LEN, DBSession
from ..models.users import  User
from ..models.groups import GROUPS_USERS, Group
from ..models.storages import VCS_ENGINES, Storage, StorageUser, StorageGroup
from ..models.projects import Project, ProjectProcessing, ProjectProcessingFile
from ..models.projects import ProjectUser, ProjectGroup
from ..models.projects import ProjectPack, ProjectPackFile


# =============================================================================
def get_action(request):
    """Return a tuple such as ``(action, items)`` where ``action`` is a
    string such as ``<act><?|!><item_id>`` and ``items`` is a list of
    selected items in a list form.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :return: (tuple)
        A tuple such as ``(action, items)``.

    Each submit button returns a string such as ``<act><?|!><item_id>.x`` where
    ``<item_id>`` is the item identifier or ``#`` for all selected items,
    ``<?|!>`` means respectively *confirm* or *proceed* and ``<act>`` is one of
    the following action:

    * ``agp``: add groups
    * ``aur``: add users
    * ``bld``: build
    * ``ccl``: cancel
    * ``cls``: close
    * ``del``: delete
    * ``des``: description
    * ``dif``: get diff
    * ``dir``: make directory
    * ``dnl``: download
    * ``exp``: export
    * ``imp``: import
    * ``npk``: create a new pack with selection
    * ``pck``: add to pack
    * ``prc``: add to processing
    * ``ren``: rename
    * ``rgp``: remove groups
    * ``rur``: remove users
    * ``rmv``: remove
    * ``sch``: search
    * ``shw``: show
    * ``syn``: synchronize
    * ``upl``: upload

    Checkbox inputs return string such as ``#<item_id>``.

    For instance, ``del!#`` and ``['#user1', '#user2']`` means "delete
    ``user1`` and ``user2``". ``syn!DataHg`` means "synchronize
    ``DataHg`` and only this one".
    """
    action = ''
    items = []
    for param in request.params:
        if param[0] == '#':
            items.append(param[1:])
        elif param[-2:] == '.x':
            if param[-3:-2] == '#':
                action = param[0:-2]
            else:
                return param[0:-2], (param[4:-2],)
    if '#' in action and not items:
        request.session.flash(_('Select items!'), 'alert')
        action = ''
    return action, items


# =============================================================================
def paging_users(request, only_active=True):
    """Return a :class:`~.renderer.Paging` object filled with users.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param only_active: (boolean, default=True)
        if ``True``, only active users are included.
    :return: (tuple)
        A tuple such as ``(paging, filters)`` where ``paging`` is a
        :class:`~.renderer.Paging` object and ``filters`` a dictionary of
        filters.
    """
    # Parameters
    paging_id = only_active and 'users' or 'users!'
    params = Paging.params(request, paging_id, '+login')
    if only_active or (len(request.POST) == 0 and not 'f_status' in params):
        params['f_status'] = 'active'

    # Query
    query = DBSession.query(User.user_id, User.login, User.name, User.status)
    if 'f_login' in params:
        query = query.filter(
            User.login.like('%%%s%%' % params['f_login'].lower()))
    if 'f_name' in params:
        query = query.filter(User.name.ilike('%%%s%%' % params['f_name']))
    if 'f_status' in params and params['f_status'] != '*':
        query = query.filter(User.status == params['f_status'])
    if 'f_group' in params:
        query = query.join(GROUPS_USERS).filter(
            GROUPS_USERS.c.group_id == params['f_group'])

    # Order by
    oby = 'users.%s' % params['sort'][1:]
    query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

    return Paging(request, paging_id, query), params


# =============================================================================
def paging_groups(request, paging_id='groups'):
    """Return a :class:`~.renderer.Paging` object filled with groups.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param paging_id: (string, default='groups')
        Paging ID: ``'groups'`` for adding purpose and ``groups!`` for
        administration purpose.
    :return: (tuple)
        A tuple such as ``(paging, filters)`` where ``paging`` is a
        :class:`~.renderer.Paging` object and ``filters`` a dictionary of
        filters.
    """
    # Parameters
    params = Paging.params(request, paging_id, '+label')

    # Query
    query = DBSession.query(Group)
    if 'f_label' in params:
        query = query.filter(Group.label.ilike('%%%s%%' % params['f_label']))

    # Order by
    oby = 'groups.%s' % params['sort'][1:]
    query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

    return Paging(request, paging_id, query), params


# =============================================================================
def current_storage(request, storage_id=None, only_dict=True):
    """Initialize, if necessary, ``request.session['storage']`` and
    return it as current storage dictionary.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param storage_id: (integer, optional)
        ID of storage to get context.
    :param only_dict: (boolean, default=True)
        If ``False``, it returns the entire
        :class:`~.models.storages.Storage` object.
    :return: (tuple)
        A tuple such as ``(storage_dictionary, handler)`` or a
        :class:`pyramid.httpexceptions.`HTTPNotFound` exception.

    ``storage_dictionary`` has the following keys: ``storage_id``,
    ``label``, ``description``, ``perm``, ``vcs_engine``, ``vcs_url``,
    ``public_url``.
    """
    # Already in session
    storage_id = storage_id or request.matchdict['storage_id']
    if only_dict and 'storage' in request.session and request\
           .session['storage']['storage_id'] == storage_id:
        handler = request.registry['handler'].get_handler(storage_id)
        if handler is not None:
            return request.session['storage'], handler

    # Read in database
    storage = DBSession.query(Storage).filter_by(
        storage_id=storage_id).first()
    if storage is None:
        raise HTTPNotFound(comment=_('This storage does not exist!'))

    # Permission
    user_id = request.session['user_id']
    perm = (has_permission(request, 'stg_editor') or storage.access == 'open')\
           and 'editor'
    if perm != 'editor':
        record = DBSession.query(StorageUser).filter_by(
            storage_id=storage_id, user_id=user_id).first()
        perm = record and record.perm
    if perm != 'editor':
        groups = [k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
        if groups:
            record = [k[0] for k in DBSession.query(StorageGroup.perm)
                .filter(StorageGroup.storage_id == storage_id)
                .filter(StorageGroup.group_id.in_(groups))]
            perm = ('editor' in record and 'editor') or (record and record[0])\
                   or perm
    if perm is None:
        raise HTTPForbidden(comment=_(
            'You do not have access to this storage!'))

    request.session['storage'] = {
        'storage_id': storage_id,
        'label': storage.label,
        'description': storage.description,
        'perm': perm,
        'vcs_engine': VCS_ENGINES[storage.vcs_engine],
        'vcs_url': storage.vcs_url,
        'public_url': storage.public_url}
    handler = request.registry['handler'].get_handler(storage_id, storage)
    return only_dict and (request.session['storage'], handler) \
           or (storage, handler)


# =============================================================================
def vcs_user(request, storage):
    """Return a VCS user tuple.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param storage: (dictionary)
        Storage dictionary.
    :return: (tuple)
        A VCS user tuple ``(user_id, password, name)``.
    """
    user = DBSession.query(StorageUser).filter_by(
        storage_id=storage['storage_id'],
        user_id=request.session['user_id']).first()
    if user is None:
        return None, None, request.session['name']
    password = decrypt(
        user.vcs_password, request.registry.settings['auth.key'])
    return user.vcs_user, password, request.session['name']


# =============================================================================
def file_infos(request, record):
    """Return a dictionary of file informations.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param record: (:class:`~.models.projects.ProjectProcessing`
        or :class:`~.models.projects.ProjectPack` instance).
    :return: (dictionary)
        A dictionary with keys ``file``, ``resource`` and ``template``. Each
        value of this dictionary is a tuple of tuples such as ``(file_type,
        storage_id, path, target, visible)``.
    """
    root_path = request.registry.settings['storage.root']
    files = {'file': [], 'resource': [], 'template': []}
    for item in record.files:
        files[item.file_type].append((
            get_mime_type(join(root_path, item.path))[1],
            item.path.partition('/')[0], item.path.partition('/')[2],
            item.target, hasattr(item, 'visible') and item.visible))
    return files


# =============================================================================
def file_download(request, path, filenames, download_name=None):
    """Prepare file for download and return a Pyramid response.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param path: (string)
        Absolute path to files.
    :param filenames: (list)
        List of files to download.
    :param download_name: (string)
        Visible name during download.
    :return: (:class:`pyramid.response.Response` instance or raise a
        :class:`pyramid.httpexceptions.HTTPNotFound` exception.)
    """
    # Single file
    if len(filenames) == 1 and isfile(join(path, filenames[0])):
        fullname = join(path, filenames[0])
        if not exists(fullname):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        with open(fullname, 'r') as hdl:
            content = hdl.read()
        download_name = download_name or filenames[0]
        response = Response(content, content_type=get_mime_type(fullname)[0])
        response.headerlist.append(('Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # Several files
    tmp = tempfile.NamedTemporaryFile(
        dir=request.registry.settings['temporary_dir'])
    zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name in filenames:
        fullname = normpath(join(path, name))
        if not fullname.startswith(path) or not exists(fullname):
            zip_file.close()
            raise HTTPNotFound(comment=_('This file does not exist!'))
        if isfile(fullname):
            zip_file.write(fullname, name)
            continue
        for root, dirs, files in walk(fullname):
            for name in dirs:
                if name in EXCLUDED_FILES:
                    dirs.remove(name)
            for name in files:
                if not name in EXCLUDED_FILES:
                    name = join(root, name)
                    try:
                        zip_file.write(name, relpath(name, path))
                    except IOError, err:
                        raise HTTPNotFound(comment=err)
    zip_file.close()
    if not download_name:
        download_name = \
            filenames[0] if len(filenames) == 1 else basename(path)
    return file_download(request, '', (tmp.name,), '%s.zip' % download_name)


# =============================================================================
def create_pack(request, filenames, path='.'):
    """Create a new pack with selected files.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param filenames: (list)
        Names of files to add to new pack.
    :param path: (string, optional)
        Common path.
    :return: (tuple)
        A tuple such as ``(project_id, pack_id``) or ``(None, None)`` if
        failed.
    """
    label = ', '.join([basename(k) for k in filenames])
    project_id = request.session['project']['project_id']
    if DBSession.query(ProjectPack) \
           .filter_by(project_id=project_id, label=label).first():
        request.session.flash(_('This pack already exists.'), 'alert')
        return None, None

    pack = ProjectPack(project_id, label)
    for name in filenames:
        pack.files.append(
            ProjectPackFile('file', normpath(join(path, name))))
        DBSession.add(pack)
        DBSession.commit()
    return pack.project_id, pack.pack_id


# =============================================================================
def add2container(request, container_type, file_type, path, filenames):
    """Add files to a processing or a pack.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param container_type: ('prc' or 'pck')
        ``'prc'`` for processing and ``'pck'`` for pack.
    :param file_type: ('fil', 'rsc', 'tpl', 'out')
        ``'fil'`` for file,``'rsc'`` for resource, ``'tpl'`` for template and
        ``'out'`` for output directory.
    :param path:
        Relative path from storage root.
    :param filenames: (list)
        Names of files to add.
    """
    if not 'container' in request.session:
        return
    project_id = request.session['container']['project_id']
    file_type = {'fil': 'file', 'rsc': 'resource', 'tpl': 'template',
                 'out': 'output'}[file_type]
    # Output
    if file_type == 'output':
        if len(filenames) > 1:
            request.session.flash(_('Select only one directory!'), 'alert')
            return
        name = join(
            request.registry.settings['storage.root'], path, filenames[0])
        if isfile(name):
            filenames[0] = dirname(filenames[0])
        record = DBSession.query(ProjectProcessing).filter_by(
            project_id=project_id, processing_id=request
            .session['container']['processing_id']).first()
        if record is not None:
            record.output = normpath(join(path, filenames[0]))
            DBSession.commit()
            request.session.flash(_(
                'Output directory has been changed to "${n}".',
                {'n': record.output}), 'message')
        return

    # Container
    if container_type == 'pck':
        record = DBSession.query(ProjectPack).filter_by(
            project_id=project_id,
            pack_id=request.session['container']['pack_id']).first()
        container_class = ProjectPackFile
    else:
        record = DBSession.query(ProjectProcessing).filter_by(
            processing_id=request.session['container']['processing_id'],
            project_id=project_id).first()
        container_class = ProjectProcessingFile
    if record is None:
        return
    paths = [k.path for k in record.files if k.file_type == file_type]

    # Browse files
    added = []
    for name in filenames:
        name = normpath(join(path, name))
        if name in paths:
            continue
        record.files.append(container_class(file_type, name))
        added.append(name)
    DBSession.commit()

    # Message
    if len(added) > 0:
        record = {'a': ', '.join(added)}
        added = {'file': _('Files to process added: ${a}', record),
                 'resource': _('Resource files added: ${a}', record),
                 'template': _('Template files added: ${a}', record)
                 }[file_type]
        request.session.flash(added, 'message')


# =============================================================================
def current_project(request, project_id=None, only_dict=True):
    """Update ``request.session['project']`` and return it as current project
    dictionary or return a SqlAlchemy object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (integer, optional)
        ID of project to get context.
    :param only_dict: (boolean, default=True)
        If ``False``, it returns the entire :class:`~.models.projects.Project`
        object.
    :return: (dictionary or ``None``)
        ``None`` if error or a dictionary with the following keys:
        ``project_id``, ``label``, ``description``, ``perm``, ``deadline``,
        ``processing_id`` (default processing ID) and ``processing_labels``.
    """
    # Already in session
    project_id = project_id or request.matchdict.get('project_id')
    if project_id is None:
        raise HTTPNotFound(comment=_('You must specify a project ID!'))
    project_id = int(project_id)

    if only_dict and 'project' in request.session \
           and request.session['project']['project_id'] == project_id:
        if 'processing_id' in request.params:
            request.session['project']['processing_id'] = \
                int(request.params['processing_id'])
        return request.session['project']

    # Read in database
    project = DBSession.query(Project).filter_by(project_id=project_id).first()
    if project is None:
        raise HTTPNotFound(comment=_('This project does not exist!'))
    processing_labels = DBSession.query(
        ProjectProcessing.processing_id, ProjectProcessing.label)\
        .filter_by(project_id=project_id)\
        .order_by(ProjectProcessing.label).all()

    # Permission?
    user_id = request.session['user_id']
    perm = has_permission(request, 'prj_editor') and 'editor'
    if perm != 'editor':
        record = DBSession.query(ProjectUser).filter_by(
            project_id=project_id, user_id=user_id).first()
        perm = record and record.perm
    if perm != 'editor':
        groups = [k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
        if groups:
            record = [k[0] for k in DBSession.query(ProjectGroup.perm)
                .filter(ProjectGroup.project_id == project_id)
                .filter(ProjectGroup.group_id.in_(groups))]
            perm = ('editor' in record and 'editor') or (record and record[0])\
                   or perm
    if perm is None:
        raise HTTPForbidden(comment=_('You do not work in this project!'))

    request.session['project'] = {'project_id': project_id,
        'label': project.label, 'description': project.description,
        'perm': perm,
        'deadline': project.deadline,
        'processing_id': int(request.params.get('processing', 1)),
        'processing_labels': processing_labels}
    return only_dict and request.session['project'] or project


# =============================================================================
def current_processing(request, project_id=None, processing_id=None,
                       container=False):
    """Return the current processing object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (integer, optional)
        ID of project to retrieve processing.
    :param processing_id: (integer, optional)
        ID of processing to retrieve.
    :param container: (boolean)
        If ``True``, add current processing container.
    :return: (tuple)
        A tuple such as ``(processing, processor)``.

    ``processing`` is a :class:`~.models.projects.ProjectProcessing`
    object. ``processor`` is a :class:`lxml.etree.ElementTree` object
    representing the used processor. If this function fails, it raises a
    :class:`pyramid.httpexceptions.`HTTPNotFound` exception.

    ``request.session['container']`` is updated with ``processing_id``,
    ``processing_label`` and ``has_output``.
    """
    # IDs
    project_id = project_id or request.matchdict.get('project_id')
    if project_id is None:
        raise HTTPNotFound(comment=_('You must specify a project ID!'))
    processing_id = processing_id or request.matchdict.get('processing_id')
    if processing_id is None:
        raise HTTPNotFound(comment=_('You must specify a processing ID!'))
    project_id = int(project_id)
    processing_id = int(processing_id)

    # Processing
    processing = DBSession.query(ProjectProcessing).filter_by(
        project_id=project_id, processing_id=processing_id).first()
    if processing is None:
        raise HTTPNotFound(comment=_('This processing does not exist!'))

    # Container for storage
    if container:
        request.session['container'] = {
            'project_id': project_id,
            'processing_id': processing_id,
            'processing_label': processing.label,
            'has_output': bool(processing.output)}

    # Processor
    processor = request.registry['fbuild'].processor(
        request, processing.processor)
    if processor is None:
        raise HTTPNotFound(comment=_('This processor does not exist!'))

    return processing, processor


# =============================================================================
def variable_schema(processor, variables, only_visible=False,
                    with_default=True):
    """Return a schema to validate variable form.

    :param processor: (:class:`lxml.etree.ElementTree` instance)
        Processor of current processing.
    :param variables: (dictionary)
        Variables of current processing.
    :param only_visible: (boolean, default=False)
        If ``True``, process only visible variables.
    :param with_default: (boolean, default=True)
        If ``True``, create schema for default values.
    :return: (tuple)
        A tuple such as ``(schema, defaults)`` where ``schema`` is a
        :class:`colander.SchemaNode` instance and ``defaults`` a dictionary.
    """
    def node(name, var):
        """Return a SchemaNode according to ``var`` type."""
        var_type = var.get('type')
        if var_type == 'boolean':
            node = SchemaNode(Boolean(), name=name, missing=False)
        elif var_type == 'integer':
            node = SchemaNode(Integer(), name=name, missing=0)
        elif var_type == 'select':
            options = [k.get('value', k.text) for k in var.findall('option')]
            node = SchemaNode(String(), name=name, validator=OneOf(options))
        elif var_type == 'regex':
            node = SchemaNode(String(), name=name, validator=All(
                Regex(var.findtext('pattern').strip()), Length(max=VALUE_LEN)))
        else:
            node = SchemaNode(String(), name=name,
                validator=Length(max=VALUE_LEN), missing='')
        return node

    schema = SchemaNode(Mapping())
    form_defaults = {}
    for var in processor.findall('processor/variables/group/var'):
        name = var.get('name')
        if only_visible \
               and (not name in variables or not variables[name].visible):
            continue

        schema.add(node(name, var))
        form_defaults[name] = variables[name].value if name in variables \
                              else var.findtext('default') is not None \
                              and var.findtext('default').strip() or ''
        if var.get('type') == 'boolean':
            form_defaults[name] = (form_defaults[name] == 'true')

        if not only_visible:
            schema.add(
                SchemaNode(Boolean(), name='%s_see' % name, missing=False))
            form_defaults['%s_see' % name] = \
                (name in variables and variables[name].visible) \
                or var.get('visible') or False

        if with_default:
            schema.add(node('%s_def' % name, var))
            form_defaults['%s_def' % name] = \
                variables[name].default if name in variables \
                else var.findtext('default') is not None \
                and var.findtext('default').strip() or ''
            if var.get('type') == 'boolean':
                form_defaults['%s_def' % name] = (
                    form_defaults['%s_def' % name] == 'true')

    return schema, form_defaults


# =============================================================================
def describe_var(request, processor, variables, name,
                 show_processor_default=False):
    """Return a description of variable ``name``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param processor: (:class:`lxml.etree.ElementTree` instance)
        Processor of current processing.
    :param variables: (dictionary)
        Variables of current processing.
    :param name: (string)
        Name of the variable.
    :param show_processor_default: (boolean, default=False)
        Show the processor default value if any.
    :return: (string)
    """
    var = processor.xpath('processor/variables/group/var[@name="%s"]' % name)
    if not len(var):
        return
    var = var[0]
    translate = get_localizer(request).translate

    html = grid_item(
        '', translate(_('Name:')), literal('<b>%s</b>' % name), class_='')
    html += grid_item(
        '', translate(_('Type:')), var.get('type'), class_='')
    if name in variables:
        html += grid_item(
            '', translate(_('Value:')), variables[name].value, class_='')
        html += grid_item(
            '', translate(_('Suggested:')), variables[name].default, class_='')
    if show_processor_default and var.findtext('default') is not None:
        html += grid_item(
            '', translate(_('Default:')), var.findtext('default'), class_='')

    description = ''
    if var.find('description') is not None:
        description += local_text(var, 'description', request)\
                       .replace(' --', '<br/>')
    if var.getparent().find('description') is not None:
        description += '<br/><br/>'
        description += local_text(var.getparent(), 'description', request) \
                     .replace(' --', '<br/>')
    if description:
        html += grid_item(
            '', translate(_('Description:')), literal(description), class_='')

    return html
