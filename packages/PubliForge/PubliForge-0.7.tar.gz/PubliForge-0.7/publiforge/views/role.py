# $Id: role.py daa7613245c8 2012/07/26 12:57:26 patrick $
# pylint: disable = I0011, C0322
"""Role view callables."""

from sqlalchemy import desc
from colander import Mapping, SchemaNode
from colander import String, Length

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from ..lib.utils import _, normalize_spaces
from ..lib.views import get_action, current_project
from ..lib.form import Form
from ..lib.renderer import Paging, TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN, DBSession, close_dbsession
from ..models.users import User
from ..models.projects import Project
from ..models.roles import Role, RoleUser


ROLE_SETTINGS_TABS = (_('Description'), _('Operators'))


# =============================================================================
class RoleView(object):
    """Class to manage roles."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='role_view', renderer='../Templates/rol_view.pt')
    def view(self):
        """Display role settings."""
        # Permission
        project = current_project(self._request)
        role = DBSession.query(Role).filter_by(
            role_id=int(self._request.matchdict.get('role_id'))).first()
        if role is None:
            raise HTTPNotFound()
        tab_set = TabSet(self._request, ROLE_SETTINGS_TABS)
        operators = [k.user_id for k in role.users]
        if len(operators):
            operators = DBSession.query(User.user_id, User.login, User.name)\
                .filter(User.user_id.in_(operators)).order_by(User.name).all()
        i_editor = project['perm'] == 'leader'

        self._request.breadcrumbs.add(
            _('Role settings'), replace=self._request.route_path(
                'role_edit', project_id=role.project_id, role_id=role.role_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'project': project, 'role': role, 'operators': operators,
            'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(route_name='role_create', renderer='../Templates/rol_edit.pt')
    def create(self):
        """Create a role."""
        # Permission
        project = current_project(self._request)
        if project['perm'] != 'leader':
            raise HTTPForbidden()

        # Environment
        form, tab_set = self._settings_form(None)

        # Action
        action = get_action(self._request)[0]
        if action == 'sav!' and form.validate():
            role = self._create(project['project_id'], form.values)
            if role is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'role_edit', project_id=role.project_id,
                    role_id=role.role_id))

        self._request.breadcrumbs.add(_('Role creation'))

        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'role': None,
            'operators': None, 'paging': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='role_edit', renderer='../Templates/rol_edit.pt')
    def edit(self):
        """Edit a role."""
        # Permission
        project = current_project(self._request)
        if project['perm'] != 'leader':
            raise HTTPForbidden()
        role_id = int(self._request.matchdict.get('role_id'))

        # Action
        paging = None
        action = get_action(self._request)[0]
        if action == 'aur?' \
                or (not action and 'paging_id' in self._request.GET):
            paging = self._paging_users(project['project_id'])
        elif action[0:4] == 'aur!':
            self._add_operators(project['project_id'], role_id)
        elif action[0:4] == 'rur!':
            DBSession.query(RoleUser).filter_by(
                project_id=project['project_id'], role_id=role_id,
                user_id=int(action[4:])).delete()
            DBSession.commit()

        # Environment
        role = DBSession.query(Role).filter_by(
            project_id=project['project_id'], role_id=role_id).first()
        if role is None:
            raise HTTPNotFound()
        form, tab_set = self._settings_form(role)
        operators = [k.user_id for k in role.users]
        if len(operators):
            operators = DBSession.query(User.user_id, User.login, User.name)\
                .filter(User.user_id.in_(operators)).order_by(User.name).all()

        # Save
        view_path = self._request.route_path(
            'role_view', project_id=role.project_id, role_id=role.role_id)
        if action == 'sav!' and form.validate(role):
            DBSession.commit()
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Role'), replace=view_path)

        return {
            'form': form, 'tab_set': tab_set, 'action': action,
            'project': project, 'role': role, 'operators': operators,
            'paging': paging}

    # -------------------------------------------------------------------------
    def _settings_form(self, role):
        """Return a role settings form.

        :param role: (:class:`~..models.roles.Role` instance)
            Current role object.
        :return: (tuple)
             A tuple such as ``(form, tab_set)``
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='description', missing='',
            validator=Length(max=DESCRIPTION_LEN)))
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        defaults = {}

        if role is not None:
            if  'paging' in self._request.session \
                    and 'operators' in self._request.session['paging'][1]:
                defaults.update(
                    self._request.session['paging'][1]['operators'])

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=role),
            TabSet(self._request, ROLE_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _paging_users(self, project_id):
        """Return a :class:`~.renderer.Paging` object filled with users.

        :param project_id: (string)
             ID of current project.
        :return: (:class:`~.renderer.Paging` instance)
        """
        params = Paging.params(self._request, 'operators', '+name')
        query = Project.team_query(project_id)

        if 'f_login' in params:
            query = query.filter(
                User.login.like('%%%s%%' % params['f_login'].lower()))
        if 'f_name' in params:
            query = query.filter(User.name.ilike('%%%s%%' % params['f_name']))

        oby = 'users.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'operators', query)

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``projects_roles`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return:
            (:class:`~..models.roles.Role` instance)
        """
        # Check unicity
        label = normalize_spaces(values['label'], LABEL_LEN)
        role = DBSession.query(Role).filter_by(
            project_id=project_id, label=label).first()
        if role is not None:
            self._request.session.flash(
                _('This role already exists.'), 'alert')
            return

        # Create role
        role = Role(project_id, label, values['description'])
        DBSession.add(role)
        DBSession.commit()

        return role

    # -------------------------------------------------------------------------
    def _add_operators(self, project_id, role_id):
        """Add selected users to the group.

        :param project_id: (string)
            Project ID.
        :param role_id: (string)
            Role ID.
        """
        role = DBSession.query(Role).filter_by(
            project_id=project_id, role_id=role_id).first()
        user_ids = [k.user_id for k in role.users]
        for user_id in get_action(self._request)[1]:
            user_id = int(user_id)
            if not user_id in user_ids:
                role.users.append(RoleUser(project_id, role_id, user_id))
        DBSession.commit()
