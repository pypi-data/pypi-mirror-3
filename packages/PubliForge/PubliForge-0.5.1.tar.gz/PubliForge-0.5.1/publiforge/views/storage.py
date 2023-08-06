# $Id: storage.py ada86c3ea608 2012/03/22 22:52:47 patrick $
# pylint: disable = I0011, C0322
"""Storage view callables."""

from os.path import join, isdir, dirname
from webhelpers.html import HTML
from sqlalchemy import select, desc, or_, and_
from colander import Mapping, SchemaNode, String, Integer, Length, OneOf

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from ..lib.utils import _, FILE_TYPES, has_permission, encrypt, age
from ..lib.xml import upload_configuration, export_configuration
from ..lib.views import vcs_user, paging_users, paging_groups, current_storage
from ..lib.views import get_action, file_download, create_pack, add2container
from ..lib.form import Form
from ..lib.renderer import TabSet, sortable_column, Paging
from ..models import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.users import User
from ..models.groups import GROUPS_USERS, Group
from ..models.storages import STORAGE_ACCESS, VCS_ENGINES, STORAGE_PERMS
from ..models.storages import Storage, StorageUser, StorageGroup


STORAGE_SETTINGS_TABS = (
    _('Description'), _('Authorized users'), _('Authorized groups'))
REFRESH = {
    900: _('every 15 minutes'), 1800: _('every 30 minutes'),
    3600: _('every hour'), 7200: _('every 2 hours'),
    14400: _('every 4 hours'), 28800: _('every 8 hours'),
    86400: _('every day')}


# =============================================================================
class StorageView(object):
    """Class to manage storages."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request
        self._vcs_engines = dict([(k, VCS_ENGINES[k]) for k in
            request.registry.settings['storage.available_vcs'].split()])

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_admin',
                 renderer='../Templates/stg_admin.pt',
                 permission='stg.update')
    def admin(self):
        """List storages for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'stg_manager', 'storage')
            action = ''
            del self._request.session['menu']
        elif action[0:4] == 'del!':
            self._delete_storages(items)
            action = ''
            del self._request.session['menu']
        elif action[0:4] == 'exp!':
            return self._export_storages(items)

        paging, defaults = self._paging_storages()
        form = Form(self._request, defaults=defaults)
        groups = [(k.group_id, k.label) for k in
                  DBSession.query(Group).join(StorageGroup)]

        depth = (self._request.breadcrumbs.current_path() ==
                 self._request.route_path('site_admin') and 3) or 2
        self._request.breadcrumbs.add(_('Storage administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action,
            'groups': groups, 'STORAGE_ACCESS': STORAGE_ACCESS,
            'vcs_engines': self._vcs_engines,
            'i_editor': has_permission(self._request, 'stg_editor'),
            'i_manager': has_permission(self._request, 'stg_manager')}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_index',
                 renderer='../Templates/stg_index.pt',
                 permission='stg.read')
    def index(self):
        """List authorized storages."""
        # Action
        user_id = self._request.session['user_id']
        action, items = get_action(self._request)
        if action[0:4] == 'exp!':
            return self._export_storages(items)
        elif action[0:3] == 'men':
            stg_user = DBSession.query(StorageUser).filter_by(
                storage_id=action[4:], user_id=user_id).first()
            if stg_user is None:
                stg_user = StorageUser(action[4:], user_id)
                DBSession.add(stg_user)
            stg_user.in_menu = action[3] == '+'
            DBSession.commit()
            del self._request.session['menu']
        elif action == 'cls!' and 'container' in self._request.session:
            del self._request.session['container']

        # Form and environment
        paging, defaults = self._paging_storages(user_id)
        form = Form(self._request, defaults=defaults)
        changes = {}
        for storage in paging:
            handler = self._request.registry['handler']\
                  .get_handler(storage.storage_id, storage)
            changes[handler.uid] = list(handler.vcs.last_change())
            changes[handler.uid][0] = age(changes[handler.uid][0])
            force = (action == 'syn!%s' % storage.storage_id) or \
                    (action == 'syn!#' and storage.storage_id in items)
            if handler.synchronize(self._request, force):
                handler.cache.clear()
        in_menus = [k[0] for k in DBSession.query(StorageUser.storage_id)
                    .filter_by(user_id=self._request.session['user_id'])
                    .filter_by(in_menu=True).all()]

        # Working?
        action, progress = \
            self._request.registry['handler'].progress(changes.keys())
        if action and not 'ajax' in self._request.params:
            self._request.response.headerlist.append(('Refresh',
                self._request.registry.settings.get('refresh.long', '8')))

        self._request.breadcrumbs.add(_('All storages'),
            'container' in self._request.session and 6 or 2)
        return {
            'form': form, 'paging': paging, 'progress': progress,
            'vcs_engines': self._vcs_engines, 'changes': changes,
            'in_menus': in_menus}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_index_ajax', renderer='json',
                 permission='stg.read')
    def index_ajax(self):
        """Authorized storage status for AJAX request."""
        user_id = self._request.session['user_id']
        paging = self._paging_storages(user_id)[0]
        working, progress = self._request.registry['handler'].progress(
            [k.storage_id for k in paging])
        response = dict([(k, progress[k][0]) for k in progress])
        response['working'] = working
        return response

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_view',
                 renderer='../Templates/stg_view.pt',
                 permission='stg.read')
    def view(self):
        """Show storage settings with its users and groups."""
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_storages((
                self._request.matchdict.get('storage_id'),))

        storage = current_storage(self._request, only_dict=False)[0]
        tab_set = TabSet(self._request, STORAGE_SETTINGS_TABS)
        members = DBSession.query(
            User.user_id, User.login, User.name, StorageUser.perm)\
            .join(StorageUser)\
            .filter(StorageUser.storage_id == storage.storage_id)\
            .filter(StorageUser.perm != None).order_by(User.login)
        member_groups = DBSession.query(
            Group.group_id, Group.label, StorageGroup.perm)\
            .filter(StorageGroup.storage_id == storage.storage_id)\
            .filter(Group.group_id == StorageGroup.group_id)\
            .order_by(Group.label).all()
        i_editor = has_permission(self._request, 'stg_editor') \
            or self._request.session['storage']['perm'] == 'editor'

        self._request.breadcrumbs.add(
            _('Storage settings'), replace=self._request.route_path(
            'storage_edit', storage_id=storage.storage_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'perms': STORAGE_PERMS, 'vcs_engines': self._vcs_engines,
            'storage': storage, 'members': members,
            'member_groups': member_groups, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_create',
                 renderer='../Templates/stg_edit.pt',
                 permission='stg.create')
    def create(self):
        """Create a storage."""
        form, tab_set = self._settings_form()

        if form.validate():
            storage = self._create(form.values)
            if storage is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'storage_edit', storage_id=storage.storage_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('Storage creation'))
        return {
            'form': form, 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'perms': STORAGE_PERMS, 'vcs_engines': self._vcs_engines,
            'storage': None, 'members': None, 'group_members': None,
            'paging': None, 'groups': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_edit',
                 renderer='../Templates/stg_edit.pt')
    def edit(self):
        """Edit storage settings."""
        # Authorization
        storage = current_storage(self._request, only_dict=False)[0]
        if not has_permission(self._request, 'stg_editor') \
               and self._request.session['storage']['perm'] != 'editor':
            raise HTTPForbidden()

        # Action
        paging = groups = None
        action = get_action(self._request)[0]
        if action == 'aur?' or \
               (not action and self._request.GET.get('paging_id') == 'users'):
            groups = DBSession.query(Group.group_id, Group.label).all()
            paging = paging_users(self._request)[0]
        elif action[0:4] == 'aur!':
            self._add_members(storage)
        elif action[0:4] == 'rur!':
            DBSession.query(StorageUser).filter_by(
                storage_id=storage.storage_id, user_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            del self._request.session['menu']
        elif action == 'agp?' or (not action and
                self._request.GET.get('paging_id') == 'groups'):
            paging = paging_groups(self._request)[0]
        elif action[0:4] == 'agp!':
            self._add_member_groups(storage)
        elif action[0:4] == 'rgp!':
            DBSession.query(StorageUser).filter_by(
                storage_id=storage.storage_id, user_id=int(action[4:]),
                perm=None).delete()
            DBSession.query(StorageGroup).filter_by(
                storage_id=storage.storage_id, group_id=action[4:]).delete()
            DBSession.commit()
            del self._request.session['menu']

        # Environment
        form, tab_set = self._settings_form(storage)
        members = DBSession.query(
            User.user_id, User.login, User.name, StorageUser.perm)\
            .filter(StorageUser.storage_id == storage.storage_id)\
            .filter(User.user_id == StorageUser.user_id)\
            .order_by(User.login).all()
        member_groups = DBSession.query(
            Group.group_id, Group.label, StorageGroup.perm)\
            .filter(StorageGroup.storage_id == storage.storage_id)\
            .filter(Group.group_id == StorageGroup.group_id)\
            .order_by(Group.label).all()

        # Save
        view_path = self._request.route_path('storage_view',
            storage_id=storage.storage_id)
        if action == 'sav!' and form.validate(storage):
            storage.set_vcs_password(self._request.registry.settings,
                form.values.get('password'))
            for user in storage.users:
                user.perm = form.values['usr_%d' % user.user_id]
            for group in storage.groups:
                group.perm = form.values['grp_%s' % group.group_id]
            DBSession.commit()
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Storage settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'perms': STORAGE_PERMS, 'vcs_engines': self._vcs_engines,
            'storage': storage, 'members': members,
            'member_groups': member_groups, 'paging': paging, 'groups': groups}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_root',
                 renderer='../Templates/stg_browse.pt',
                 permission='stg.read')
    @view_config(route_name='storage_browse',
                 renderer='../Templates/stg_browse.pt',
                 permission='stg.read')
    def browse(self):
        """Browse a storage."""
        # Environment
        storage, handler = current_storage(self._request)
        storage_id = storage['storage_id']
        path = self._request.matchdict.get('path', [])
        path, real_path, html_path = self._html_path(storage_id, path)

        # Form, action & working status
        form, action, items, working = \
            self._browse_action(storage, handler, path)
        if action[0:4] == 'dnl!':
            return file_download(self._request, real_path, items)
        elif action[0:4] == 'sch!':
            return HTTPFound(self._request.route_path('file_search'))
        elif action[0:4] == 'npk!' and items[0] is not None:
            return HTTPFound(self._request.route_path(
                'pack_edit', project_id=items[0], pack_id=items[1]))

        # Directory content
        dirs, files = handler.dir_infos(
            path, self._request.params.get('sort', '+name'))

        # Working?
        working, progress = self._request\
            .registry['handler'].progress((storage_id,), working)
        if working and not 'ajax' in self._request.params:
            self._request.response.headerlist.append(('Refresh',
                self._request.registry.settings.get('refresh.short', '3')))
        if working:
            handler.cache.clear()
        if storage_id in progress and progress[storage_id][0] == 'error':
            self._request.session.flash(progress[storage_id][1], 'alert')

        self._request.breadcrumbs.add(_('Storage browsing'), root_chunks=3)
        return {
            'form': form, 'action': action, 'working': working,
            'sortable_column': sortable_column, 'storage': storage,
            'path': path, 'html_path': html_path, 'dirs': dirs,
            'files': files, 'FILE_TYPES': FILE_TYPES,
            'vcs_engines': self._vcs_engines}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_root_ajax', renderer='json',
                 permission='stg.read')
    @view_config(route_name='storage_browse_ajax', renderer='json',
                 permission='stg.read')
    def browse_ajax(self):
        """Browse a storage for AJAX request."""
        storage_id = self._request.matchdict['storage_id']
        working = self._request.registry['handler'].progress((storage_id,))[0]
        return {'working': working}

    # -------------------------------------------------------------------------
    def _paging_storages(self, user_id=None):
        """Return a :class:`~..lib.renderer.Paging` object filled
        with storages.

        :param user_id: (integer, optional)
            Select only storages of user ``user_id``.
        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.renderer.Paging` object and ``filters`` a
            dictionary  of filters.
        """
        # Parameters
        paging_id = user_id is None and 'storages!' or 'storages'
        params = Paging.params(self._request, paging_id, '+storage_id')
        if user_id is not None and 'f_access' in params:
            del params['f_access']

        # Query
        query = DBSession.query(Storage)
        if user_id is not None:
            groups = [k.group_id for k in DBSession.execute(
                select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
            if groups:
                query = query.filter(or_(
                    Storage.access == 'open',
                    and_(StorageUser.user_id == user_id,
                         StorageUser.perm != None,
                         StorageUser.storage_id == Storage.storage_id),
                    and_(StorageGroup.group_id.in_(groups),
                         StorageGroup.storage_id == Storage.storage_id))
                    ).distinct(Storage.storage_id, Storage.label)
            else:
                query = query.join(StorageUser).filter(or_(
                    Storage.access == 'open',
                    and_(StorageUser.user_id == user_id,
                         StorageUser.perm != None)))
        elif 'f_login' in params:
            query = query.join(StorageUser).join(User)\
                    .filter(User.login == params['f_login'])\
                    .filter(StorageUser.perm != None)
        if 'f_id' in params:
            query = query.filter(Storage.storage_id.ilike(
                '%%%s%%' % params['f_id']))
        if 'f_group' in params:
            query = query.join(StorageGroup).filter(
                StorageGroup.group_id == params['f_group'])
        if 'f_label' in params:
            query = query.filter(
                Storage.label.ilike('%%%s%%' % params['f_label']))
        if 'f_access' in params and params['f_access'] != '*':
            query = query.filter(Storage.access == params['f_access'])
        elif not 'f_access' in params:
            query = query.filter(Storage.access != 'closed')
        if 'f_engine' in params:
            query = query.filter(Storage.vcs_engine == params['f_engine'])

        # Order by
        oby = 'storages.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, paging_id, query), params

    # -------------------------------------------------------------------------
    def _delete_storages(self, storage_ids):
        """Delete storages.

        :param storage_ids: (list)
            List of storage IDs to delete.
        """
        if not has_permission(self._request, 'stg_manager'):
            raise HTTPForbidden()
        storage_root = self._request.registry.settings['storage.root']
        for storage_id in storage_ids:
            Storage.delete(storage_root, storage_id)

    # -------------------------------------------------------------------------
    def _export_storages(self, storage_ids):
        """Export storages.

        :param storage_ids: (list)
            List of storage IDs to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        i_editor = has_permission(self._request, 'stg_editor')
        user_id = self._request.session['user_id']
        groups = set([k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))])
        elements = []
        for storage in DBSession.query(Storage)\
                .filter(Storage.storage_id.in_(storage_ids))\
                .order_by('label'):
            if i_editor or storage.access == 'open' \
                   or user_id in [k.user_id for k in storage.users] \
                   or (groups and
                       groups & set([k.group_id for k in storage.groups])):
                elements.append(storage.xml())

        name = '%s_storages.pfs' % self._request.registry.settings.get(
            'skin.label', 'publiforge')
        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, storage=None):
        """Return a storage settings form.

        :param storage: (:class:`~..models.storages.Storage` instance,
            optional) Current storage object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``.
        """
        vcs_engine = storage and storage.vcs_engine \
                     or self._request.params.get('vcs_engine')

        # Schema
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='access',
            validator=OneOf(STORAGE_ACCESS.keys())))
        if storage is None:
            schema.add(SchemaNode(String(), name='storage_id',
                validator=Length(max=ID_LEN)))
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        if storage is None:
            schema.add(SchemaNode(String(), name='vcs_engine',
                validator=OneOf(self._vcs_engines.keys())))
        if vcs_engine is None or vcs_engine not in ('none', 'local'):
            schema.add(SchemaNode(String(), name='vcs_url',
                validator=Length(max=PATH_LEN)))
            schema.add(SchemaNode(String(), name='vcs_user',
                validator=Length(max=ID_LEN)))
            schema.add(SchemaNode(String(), name='password', missing=None))
        if vcs_engine is None or vcs_engine in ('none', 'local'):
            schema.add(SchemaNode(String(), name='public_url',
                validator=Length(max=PATH_LEN), missing=None))
        schema.add(SchemaNode(Integer(), name='refresh', missing=3600))
        if storage is not None:
            for user in storage.users:
                schema.add(SchemaNode(String(), name='usr_%d' % user.user_id,
                validator=OneOf(STORAGE_PERMS.keys())))
            for group in storage.groups:
                schema.add(SchemaNode(String(), name='grp_%s' % group.group_id,
                validator=OneOf(STORAGE_PERMS.keys())))

        defaults = {'access': 'open', 'vcs_engine': 'local', 'refresh': 3600}

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=storage),
            TabSet(self._request, STORAGE_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, values):
        """Create a storage.

        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.storages.Storage` instance or ``None``)
        """
        # Check existence
        storage_id = values['storage_id'].strip()
        storage = DBSession.query(Storage).filter_by(
            storage_id=storage_id).first()
        if storage is None:
            label = u' '.join(values['label'].strip().split())[0:LABEL_LEN]
            storage = DBSession.query(Storage).filter_by(
                label=label).first()
        if storage is not None:
            self._request.session.flash(
                _('This storage already exists.'), 'alert')
            return

        # Create storage
        # pylint: disable = I0011, W0142
        record = dict(
            [(k, values[k]) for k in values if hasattr(Storage, k)])
        storage = Storage(self._request.registry.settings, **record)
        storage.set_vcs_password(
            self._request.registry.settings, values.get('password'))
        DBSession.add(storage)
        DBSession.commit()

        # Clone
        handler = self._request.registry['handler'].get_handler(
            storage.storage_id, storage)
        handler.clone(self._request)

        return storage

    # -------------------------------------------------------------------------
    @classmethod
    def _save(cls, storage, values):
        """Save a storage settings.

        :param storage: (:class:`~..models.storages.Storage` instance)
            Storage to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Update permissions
        for user in storage.users:
            user.perm = values['perm_%d' % user.user_id]

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    def _add_members(self, storage):
        """Add selected users to the storage.

        :param storage_id: (:class:`~..models.storages.Storage` instance)
            Storage object.
        """
        if not has_permission(self._request, 'stg_editor') \
               and self._request.session['storage']['perm'] != 'editor':
            return

        user_ids = [k.user_id for k in storage.users]
        for user_id in get_action(self._request)[1]:
            user_id = int(user_id)
            if not user_id in user_ids:
                storage.users.append(StorageUser(
                    storage.storage_id, user_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _add_member_groups(self, storage):
        """Add selected groups to the storage.

        :param storage_id: (:class:`~..models.storages.Storage` instance)
            Storage object.
        """
        if not has_permission(self._request, 'stg_editor') \
               and self._request.session['storage']['perm'] != 'editor':
            return

        group_ids = [k.group_id for k in storage.groups]
        for group_id in get_action(self._request)[1]:
            if not group_id in group_ids:
                storage.groups.append(StorageGroup(
                    storage.storage_id, group_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _html_path(self, storage_id, path):
        """Return relative path in storage, real path and path in one string
        with ``<a>`` tags.

        :param storage_id: (string)
            Storage ID.
        :param path: (list)
            Splitted relative path inside the storage.
        :return: (tuple)
            A tuple such as ``(path, real_path, html_path)`` or a
            :class:`pyramid.httpexceptions.`HTTPNotFound` exception..
        """
        # Path exists?
        # pylint: disable = I0011, W0142
        real_path = join(self._request.registry.settings['storage.root'],
                         storage_id, *path)
        if not isdir(real_path) and path:
            real_path = dirname(real_path)
            path = path[0:-1]
        if not isdir(real_path):
            raise HTTPNotFound(comment=_('This directory does not exist!'))

        # Root path
        if len(path) == 0:
            return '', real_path, HTML.span(storage_id)

        # Other path
        html = HTML.a(storage_id, href=self._request.route_path(
            'storage_root', storage_id=storage_id))
        for index in range(len(path) - 1):
            html += ' / ' + HTML.a(path[index], href=self._request.route_path(
                'storage_browse', storage_id=storage_id,
                path='/'.join(path[0:index + 1])).decode('utf8'))
        html += ' / ' + HTML.span(path[-1])

        return join('.', *path), real_path, html

    # -------------------------------------------------------------------------
    def _browse_action(self, storage, handler, path):
        """Return form, current action and working status for browse view.

        :param storage: (dictionary)
            Storage dictionary.
        :param handler: (:class:`~..lib.handler.Handler` instance)
            Storage Control System.
        :param path:
            Relative path in storage.
        :return: (tuple)
            A tuple such as ``(form, action, items, working)``
        """
        working = False
        action, items = get_action(self._request)
        form = self._vcs_user_form(storage, action)

        # Check
        if action[0:4] in ('upl!', 'dir!', 'ren!', 'del!'):
            if storage['perm'] == 'user':
                raise HTTPForbidden()
            if not form.validate():
                action = '%s?%s' % (action[0:3], action[4:])
                return form, action, items, working

        # Action
        if action[0:4] == 'upl!':
            upload_file = self._request.params.get('upload_file')
            if not isinstance(upload_file, basestring):
                working = handler.launch(self._request, handler.upload,
                    (vcs_user(self._request, storage), path, upload_file,
                     items and items[0] or None,
                     form.values.get('message', '-')))
        elif action == 'dir!':
            working = handler.launch(
                self._request, handler.mkdir, (path, form.values['directory']))
        elif action[0:4] == 'ren!':
            working = handler.launch(self._request, handler.rename,
                (vcs_user(self._request, storage), path, action[4:],
                 form.values['new_name'], form.values.get('message', '-')))
            action = ''
        elif action[0:4] == 'del!':
            working = handler.launch(self._request, handler.remove,
                (vcs_user(self._request, storage), path, items,
                 form.values.get('message', '-')))
        elif action == 'sch!' and 'search' in self._request.session:
            del self._request.session['search']
        elif action[0:4] in ('npk!', 'cls!', 'pck!', 'prc!'):
            items = self._browse_action_container(
                action, items, join(storage['storage_id'], path), form)

        # Synchronize
        if not working:
            working = handler.synchronize(self._request, action == 'syn!')
            action = '' if working else action

        return form, action, items, working

    # -------------------------------------------------------------------------
    def _browse_action_container(self, action, items, path, form):
        """Manage container actions.

        :param action: (string)
            Action.
        :param items: (list)
            List of selected items.
        :param path: (string)
            Relative path from storage root.
        :param form: (:class:`~..lib.form.Form` instance)
            Browse form.
        :return: (tuple)
            A tuple such as ``(project_id, pack_id)`` or ``items``
        """
        # Close container
        if action == 'cls!' and 'container' in self._request.session:
            del self._request.session['container']

        # Add to container
        elif action[0:4] in ('pck!', 'prc!'):
            add2container(
                self._request, action[0:3], action[4:7], path, items)
            form.forget('#')

        # Create pack
        elif action[0:4] == 'npk!' and 'project' in self._request.session:
            return create_pack(self._request, items, path)

        return items

    # -------------------------------------------------------------------------
    def _vcs_user_form(self, storage, action):
        """Create a VCS user form and, eventually, update ``StorageUser``
        table setting up ``vcs_user`` and ``vcs_password``.

        :param storage: (dictionary)
            Storage dictionary.
        :param action: (string)
            Current action
        :return: (:class:`~.lib.form.Form` instance)
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='vcs_user',
            validator=Length(max=ID_LEN), missing=None))
        schema.add(SchemaNode(String(), name='vcs_password', missing=None))
        if 'message' in self._request.params:
            schema.add(SchemaNode(String(), name='message',
                validator=Length(max=DESCRIPTION_LEN)))
        if 'directory' in self._request.params:
            schema.add(SchemaNode(String(), name='directory',
                validator=Length(max=PATH_LEN)))
        elif action[0:4] == 'ren?' or 'new_name' in self._request.params:
            schema.add(SchemaNode(String(), name='new_name',
                validator=Length(max=PATH_LEN)))

        form = Form(self._request, schema=schema)
        if  action[0:4] == 'ren?':
            form.values['new_name'] = action[4:]
            return form
        if not form.validate() or not 'vcs_change' in self._request.params:
            return form

        user = DBSession.query(StorageUser).filter_by(
            storage_id=storage['storage_id'],
            user_id=self._request.session['user_id']).first()
        if user is None:
            user = StorageUser(storage['storage_id'],
                                 user_id=self._request.session['user_id'])
        user.vcs_user = form.values['vcs_user']
        user.vcs_password = encrypt(form.values['vcs_password'],
            self._request.registry.settings['auth.key'])
        DBSession.commit()
        self._request.session.flash(_('VCS user has been changed.'))

        return form
