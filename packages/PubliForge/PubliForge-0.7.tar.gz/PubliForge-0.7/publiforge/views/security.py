# $Id: security.py 9e4e40e2d07e 2012/08/10 10:47:30 patrick $
# pylint: disable = I0011, C0322
"""Security view callables."""

from colander import Mapping, SchemaNode, String, Boolean, Length

from pyramid.view import view_config
from pyramid.view import notfound_view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotAcceptable
from pyramid.security import forget, remember, authenticated_userid
from pyramid.security import NO_PERMISSION_REQUIRED

from ..lib.utils import _
from ..lib.views import connect_user
from ..lib.form import button, Form
from ..models import close_dbsession


# =============================================================================
def login(request):
    """This view renders a login form and processes the post checking
    credentials.
    """
    # Create form
    schema = SchemaNode(Mapping())
    schema.add(SchemaNode(String(), name='login', validator=Length(min=2)))
    schema.add(SchemaNode(String(), name='password', validator=Length(min=8)))
    schema.add(SchemaNode(Boolean(), name='remember', missing=False))
    came_from = request.params.get('came_from') \
        or (request.url != request.route_url('login') and request.url) \
        or request.route_url('home')
    form = Form(request, schema=schema, defaults={'came_from': came_from})

    # Validate form
    # pylint: disable = I0011, E1103
    if form.validate():
        user_login = form.values['login']
        password = form.values['password']
        user = connect_user(request, user_login, password)
        if not isinstance(user, int):
            user.setup_environment(request)
            max_age = (
                form.values['remember']
                and request.registry.settings.get('auth.remember', '5184000'))\
                or None
            close_dbsession(request)
            return HTTPFound(
                location=came_from,
                headers=remember(request, user.login, max_age=max_age))
        request.session.flash({
            1: _('ID or password is incorrect.'),
            2: _('Your account is not active.'),
            3: _('Your account has expired.'),
            4: _('Your IP is rejected.')}[user], 'alert')

    close_dbsession(request)
    return {'form': form}


# =============================================================================
@view_config(route_name='logout')
def logout(request):
    """This view will clear the credentials of the logged in user and redirect
    back to the login page.
    """
    request.session.clear()
    close_dbsession(request)
    return HTTPFound(
        location=request.route_path('login'), headers=forget(request))


# =============================================================================
class ErrorView(object):
    """Class to manage error page."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @notfound_view_config(renderer='../Templates/error.pt')
    @forbidden_view_config(renderer='../Templates/error.pt')
    @view_config(context=HTTPNotAcceptable, renderer='../Templates/error.pt',
                 permission=NO_PERMISSION_REQUIRED)
    def error(self):
        """This view outputs an error message or redirects to login page."""
        status = self._request.exception.status_int
        if status in (401, 403) \
                and authenticated_userid(self._request) is None:
            return HTTPFound(self._request.route_path(
                'login', _query=(('came_from', self._request.path),)))

        self._request.response.status = status
        self._request.breadcrumbs.add(_('Error ${status}', {'status': status}))
        return {
            'button': button,
            'message': self._request.exception.comment or {
                403: _('Access was denied to this resource.'),
                404: _('The resource could not be found.'),
                406: _('The server could not comply with the request since'
                       ' it is either malformed or otherwise incorrect.'),
                500: _('Internal Server Error.')}
            .get(status, self._request.exception.explanation)}
