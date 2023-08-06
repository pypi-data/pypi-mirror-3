# $Id: group.py e8da66c6d933 2012/02/18 22:34:11 patrick $
# pylint: disable = I0011, C0322
"""Group view callables."""

from colander import Mapping, SchemaNode, String
from colander import Length, OneOf
from sqlalchemy import desc

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPNotFound

from ..lib.utils import _, has_permission
from ..lib.xml import upload_configuration, export_configuration
from ..lib.views import get_action, paging_users
from ..lib.form import Form
from ..lib.renderer import TabSet, Paging
from ..models import LABEL_LEN, DESCRIPTION_LEN, DBSession, close_dbsession
from ..models.users import PERM_SCOPES, USER_PERMS, User
from ..models.groups import GROUPS_USERS, Group, GroupPerm


GROUP_SETTINGS_TABS = (_('Description'), _('Permissions'), _('Members'))


# =============================================================================
class GroupView(object):
    """Class to manage groups."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='group_admin',
                 renderer='../Templates/grp_admin.pt',
                 permission='grp.update')
    def admin(self):
        """List groups for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'grp_manager', 'group')
            action = ''
        elif action[0:4] == 'del!':
            self._delete_groups(items)
            action = ''
        elif action[0:4] == 'exp!':
            return self._export_groups(items)

        paging, defaults = self._paging_groups()
        form = Form(self._request, defaults=defaults)

        depth = (self._request.breadcrumbs.current_path() ==
                 self._request.route_path('site_admin') and 3) or 2
        self._request.breadcrumbs.add(_('Group administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action,
            'i_manager': has_permission(self._request, 'grp_manager')}

    # -------------------------------------------------------------------------
    @view_config(route_name='group_view', renderer='../Templates/grp_view.pt',
                 permission='grp.read')
    def view(self):
        """Show group settings."""
        group_id = self._request.matchdict.get('group_id')
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_groups((group_id,))

        group = DBSession.query(Group).filter_by(group_id=group_id).first()
        if group is None:
            raise HTTPNotFound()
        tab_set = TabSet(self._request, GROUP_SETTINGS_TABS)
        users = [k.user_id for k in group.users]
        if len(users):
            users = DBSession.query(User.user_id, User.login, User.name)\
                .filter(User.user_id.in_(users)).order_by(User.login).all()

        self._request.breadcrumbs.add(
            _('Group settings'), replace=self._request.route_path(
            'group_edit', group_id=group.group_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'PERM_SCOPES': PERM_SCOPES, 'USER_PERMS': USER_PERMS,
            'group': group, 'users': users,
            'i_modifier': has_permission(self._request, 'grp_modifier')}

    # -------------------------------------------------------------------------
    @view_config(route_name='group_create',
                 renderer='../Templates/grp_edit.pt',
                 permission='grp.create')
    def create(self):
        """Create a group."""
        form, tab_set = self._settings_form()

        if form.validate():
            group = self._create(form.values)
            if group is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'group_edit', group_id=group.group_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('Group creation'))
        return {
            'form': form, 'tab_set': tab_set,
            'PERM_SCOPES': PERM_SCOPES, 'USER_PERMS': USER_PERMS,
             'group': None, 'users': None, 'paging': None, 'groups': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='group_edit', renderer='../Templates/grp_edit.pt',
                 permission='grp.update')
    def edit(self):
        """Edit group settings."""
        # Action
        paging = groups = None
        group_id = self._request.matchdict.get('group_id')
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_groups((group_id,))
        elif action[0:4] == 'add!':
            self._add_users(group_id)
        elif action[0:7] == 'add?usr' or (not action and
                ('page_size' in self._request.params
                 or 'page' in self._request.params)):
            paging = paging_users(self._request)[0]
            groups = DBSession.query(Group.group_id, Group.label).all()
        elif action[0:7] == 'rmv!usr':
            DBSession.execute(GROUPS_USERS.delete()
                .where(GROUPS_USERS.c.group_id == group_id)
                .where(GROUPS_USERS.c.user_id == int(action[7:])))
            DBSession.commit()

        # Environment
        group = DBSession.query(Group).filter_by(group_id=group_id).first()
        if group is None:
            raise HTTPNotFound()
        form, tab_set = self._settings_form(group)
        users = [k.user_id for k in group.users]
        if len(users):
            users = DBSession.query(User.user_id, User.login, User.name)\
                .filter(User.user_id.in_(users)).order_by(User.login).all()

        # Save
        view_path = self._request.route_path('group_view',
            group_id=group.group_id)
        if action == 'sav!' and form.validate(group) \
               and self._save(group, form.values):
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Group settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'PERM_SCOPES': PERM_SCOPES, 'USER_PERMS': USER_PERMS,
            'group': group, 'users': users, 'paging': paging,
            'groups': groups}

    # -------------------------------------------------------------------------
    def _paging_groups(self):
        """Return a :class:`~..lib.renderer.Paging` object filled
        with groups.

        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.renderer.Paging` object and ``filters`` a
            dictionary of filters.
        """
        # Parameters
        params = Paging.params(self._request, 'groups!', '+label')

        # Query
        query = DBSession.query(Group)
        if 'f_label' in params:
            query = query.filter(
                Group.label.ilike('%%%s%%' % params['f_label']))

        # Order by
        oby = 'groups.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'groups!', query), params

    # -------------------------------------------------------------------------
    def _delete_groups(self, group_ids):
        """Delete groups.

        :param group_ids: (list)
            List of group IDs to delete.
        """
        if not has_permission(self._request, 'grp_manager'):
            raise HTTPForbidden()
        group_ids = set([int(k) for k in group_ids])

        # Do not delete my own groups
        user_id = self._request.session['user_id']
        ids = set([k[0] for k in DBSession.query(GROUPS_USERS.c.group_id)
                   .filter(User.user_id == user_id)
                   .filter(User.user_id == GROUPS_USERS.c.user_id).all()])
        if group_ids & ids:
            self._request.session.flash(
                _("You can't delete your own group."), 'alert')
            return

        # Delete
        DBSession.query(Group).filter(
            Group.group_id.in_(group_ids)).delete('fetch')
        DBSession.commit()

    # -------------------------------------------------------------------------
    def _export_groups(self, group_ids):
        """Export groups.

        :param group_ids: (list)
            List of group IDs to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        if not has_permission(self._request, 'grp_viewer'):
            raise HTTPForbidden()
        elements = []
        for group in DBSession.query(Group)\
                .filter(Group.group_id.in_(group_ids)).order_by('label'):
            elements.append(group.xml())

        name = '%s_groups.pfg' % self._request.registry.settings.get(
            'skin.label', 'publiforge')
        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, group=None):
        """Return a group settings form.

        :param group: (:class:`~..models.groups.Group` instance, optional)
            Current group object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``.
        """
        # Schema
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        schema.add(SchemaNode(String(), name='label',
            validator=Length(min=2, max=LABEL_LEN)))
        for scope in PERM_SCOPES:
            schema.add(SchemaNode(String(), name='perm_%s' % scope,
                validator=OneOf(USER_PERMS.keys()), missing='-'))

        # Defaults
        defaults = {}
        if group is not None:
            for perm in group.perms:
                defaults['perm_%s' % perm.scope] = perm.level

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=group),
            TabSet(self._request, GROUP_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, values):
        """Create a group.

        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.groups.Group` instance or ``None``)
        """
        # Check existence
        label = u' '.join(values['label'].strip().split())[0:LABEL_LEN]
        group = DBSession.query(Group).filter_by(label=label).first()
        if group is not None:
            self._request.session.flash(
                _('This group already exists.'), 'alert')
            return

        # Create group
        group = Group(label, values['description'])
        DBSession.add(group)
        DBSession.commit()

        # Add permissions
        for scope in PERM_SCOPES:
            scope = 'perm_%s' % scope
            if values[scope] != '-':
                group.perms.append(GroupPerm(
                    group.group_id, scope[5:], values[scope]))

        DBSession.commit()
        return group

    # -------------------------------------------------------------------------
    @classmethod
    def _save(cls, group, values):
        """Save a group settings.

        :param group: (:class:`~..models.groups.Group` instance)
            Group to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Update permissions
        perms = dict([(k.scope, k) for k in group.perms])
        for scope in PERM_SCOPES:
            if values['perm_%s' % scope] != '-':
                if not scope in perms:
                    group.perms.append(GroupPerm(
                        group.group_id, scope, values['perm_%s' % scope]))
                else:
                    perms[scope].level = values['perm_%s' % scope]
            elif scope in perms:
                DBSession.delete(perms[scope])

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    def _add_users(self, group_id):
        """Add selected users to the group.

        :param group_id: (string)
            Group ID.
        """
        group = DBSession.query(Group).filter_by(
            group_id=group_id).first()
        user_ids = [k.user_id for k in group.users]
        for user_id in get_action(self._request)[1]:
            user_id = int(user_id)
            if not user_id in user_ids:
                DBSession.execute(GROUPS_USERS.insert().values(
                    group_id=group_id, user_id=user_id))
        DBSession.commit()
        del self._request.session['menu']
