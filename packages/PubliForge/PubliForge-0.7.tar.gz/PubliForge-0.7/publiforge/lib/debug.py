# $Id: debug.py 9e4e40e2d07e 2012/08/10 10:47:30 patrick $
"""Debug or testing functions and classes."""
import logging
import cgi
import re
from subprocess import PIPE, STDOUT, Popen

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember

from .views import connect_user
from ..models import close_dbsession


LOG = logging.getLogger(__name__)


# =============================================================================
def includeme(config):
    """Include HTML validator."""
    config.add_tween('publiforge.lib.debug.htmlvalidator_tween_factory')


# =============================================================================
def htmlvalidator_tween_factory(handler, registry):
    """HTML validator tween factory.

    :param handler: (:class:`pyramid.request.Request` instance)
    :param registry: (:class:`pyramid.registry.Registry` instance)
    :return: (:class:`pyramid.response.Response` instance)
    """
    # pylint: disable = I0011, W0613
    def htmlvalidator_tween(request):
        """HTML validator tween."""
        # Is a OK HTML?
        response = handler(request)
        if response.status_int != 200 or 'html' not in response.content_type:
            return response

        # Validate
        cmd = 'xml' in response.content_type and ['validate', '--xml'] \
              or ['validate']
        error = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)\
            .communicate(response.body)[0]

        # Error?
        if error:
            error = error.decode('utf8')
            LOG.error('%s: %s' % (request.current_route_url(), error.strip()))
            error = '<pre style="background-color: #ffffdd; color: #993333;'\
                    ' border: 1px solid #993333; padding: 1ex;">%s</pre>\n' \
                    % cgi.escape(error)
            match = re.search(r'</body>', response.text, re.I)
            if match:
                response.text = u'%s%s%s' % (
                    response.text[:match.start()], error,
                    response.text[match.start():])
            else:
                response.text += error
            response.content_length = str(len(response.body))

        return response

    return htmlvalidator_tween


# =============================================================================
@view_config(route_name='login_test', permission=NO_PERMISSION_REQUIRED)
def login_test(request):
    """Quick log in for test only."""
    user_login = request.params.get('login')
    if not 'paste.testing' in request.environ or user_login is None:
        close_dbsession(request)
        return HTTPFound(location=request.route_path('login'))
    # pylint: disable = I0011, E1103
    user = connect_user(request, user_login)
    user.setup_environment(request)
    close_dbsession(request)
    return HTTPFound('/robots.txt', headers=remember(request, user.login))
