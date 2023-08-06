# $Id: security.py de5826a61f18 2012/02/27 17:59:57 patrick $
# pylint: disable = I0011, C0322
"""Security view callables."""

from datetime import datetime, date
from colander import Mapping, SchemaNode, String, Boolean, Length

from pyramid.view import view_config
from pyramid.view import notfound_view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotAcceptable
from pyramid.security import forget, remember, authenticated_userid
from pyramid.security import NO_PERMISSION_REQUIRED

from ..lib.utils import _, hash_sha
from ..lib.form import button, Form
from ..models import DBSession
from ..models.users import User


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
        user = connect(request, user_login, password)
        if not isinstance(user, int):
            user.setup_environment(request)
            max_age = (form.values['remember']
                and request.registry.settings.get('auth.remember', '5184000'))\
                or None
            DBSession.close()
            return HTTPFound(location=came_from,
                headers=remember(request, user.user_id, max_age=max_age))
        request.session.flash({
            1: _('ID or password is incorrect.'),
            2: _('Your account is not active.'),
            3: _('Your account has expired.'),
            4: _('Your IP is rejected.')}[user], 'alert')

    DBSession.close()
    return {'form': form}


# =============================================================================
@view_config(route_name='login_test', permission=NO_PERMISSION_REQUIRED)
def login_test(request):
    """Quick log in for test only."""
    user_login = request.params.get('login')
    if not 'paste.testing' in request.environ or user_login is None:
        DBSession.close()
        return HTTPFound(location=request.route_path('login'))
    # pylint: disable = I0011, E1103
    user = connect(request, user_login)
    user.setup_environment(request)
    DBSession.close()
    return HTTPFound('/robots.txt',  headers=remember(request, user.user_id))


# =============================================================================
@view_config(route_name='logout')
def logout(request):
    """This view will clear the credentials of the logged in user and redirect
    back to the login page.
    """
    request.session.clear()
    DBSession.close()
    return HTTPFound(
        location=request.route_path('login'), headers=forget(request))


# =============================================================================
@notfound_view_config(renderer='../Templates/error.pt')
@forbidden_view_config(renderer='../Templates/error.pt')
@view_config(context=HTTPNotAcceptable, renderer='../Templates/error.pt',
             permission=NO_PERMISSION_REQUIRED)
def error(request):
    """This view outputs an error message or redirects to login page."""
    status = request.exception.status_int
    if status in (401, 403) and authenticated_userid(request) is None:
        return HTTPFound(request.route_path(
            'login', _query=(('came_from', request.path),)))

    request.response.status = status
    request.breadcrumbs.add(_('Error ${status}', {'status': status}))
    DBSession.close()
    return {'button': button,
            'message': request.exception.comment or {
            403: _('Access was denied to this resource.'),
            404: _('The resource could not be found.'),
            406: _('The server could not comply with the request since it '
                   'is either malformed or otherwise incorrect.'),
            500: _('Internal Server Error.')
            }.get(status, request.exception.explanation)}


# =============================================================================
def connect(request, code, password=None):
    """If the user with ``code`` and ``password`` is authorized, it updates
    ``last_login`` field and returns an ``User`` object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param code: (string)
        Login or ID of the user to connect.
    :param password: (string, optional)
        Clear password.
    :return: (:class:`~.models.users.User` instance or integer)
        The connected user or an error code.

    If ``password`` is ``None``, password checking is not performed.

    Values of the error code are:

    * 1: incorrect user code or password
    * 2: inactive account
    * 3: expired account
    * 4: forbidden IP
    """
    # Check user
    if isinstance(code, int) and password is None:
        user = DBSession.query(User).filter_by(user_id=code).first()
    else:
        code = code.strip().lower()
        user = DBSession.query(User).filter_by(login=code).first()
    if user is None:
        return 1
    if password is not None:
        key = request.registry.settings['auth.key']
        if hash_sha(password.strip(), key) != user.password:
            return user.password is None and 2 or 1
    if user.status != 'active':
        return 2 if user.status == 'inactive' else 1
    if user.expiration and user.expiration < date.today():
        return 3
    if user.restrict_ip and not (request.environ['REMOTE_ADDR']
            in [str(k.ip) for k in user.ips]):
        return 4

    # Update last login date in database
    user.last_login = datetime.now()
    DBSession.commit()
    return user
