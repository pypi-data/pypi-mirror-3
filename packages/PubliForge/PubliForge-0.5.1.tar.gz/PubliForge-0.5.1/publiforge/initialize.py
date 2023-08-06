# $Id: initialize.py ada86c3ea608 2012/03/22 22:52:47 patrick $
"""When you launch the `PubliForge` application, this module determines which
mode you are running: front, agent or both.  According to this mode, it sets up
database, creates a instance of :class:`~.lib.build.front.FrontBuildManager`
class, an instance of :class:`~.lib.handler.HandlerManager`, an instance of
:class:`~.lib.build.agent.AgentBuildManager` class and makes required
directories.
"""

import logging
import sys
import mimetypes
from os import makedirs
from os.path import exists, join, dirname
from shutil import rmtree
from ConfigParser import ConfigParser
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from sqlalchemy import engine_from_config
from sqlalchemy.exc import ProgrammingError

from pyramid.i18n import get_localizer
from pyramid.security import Allow, Authenticated
from pyramid.security import ALL_PERMISSIONS, NO_PERMISSION_REQUIRED
from pyramid.threadlocal import get_current_request
from pyramid.renderers import get_renderer
from pyramid.events import NewRequest, BeforeRender
from pyramid_beaker import session_factory_from_settings

from .lib.utils import _
from .lib.renderer import Breadcrumbs, Menu
from .lib.handler import HandlerManager
from .lib.build.front import FrontBuildManager
from .lib.build.agent import AgentBuildManager
from .models import DBSession, Base
from .models.processors import Processor
from .views.security import connect


LOG = logging.getLogger(__name__)


# =============================================================================
class Initialize(object):
    """Initialization application class."""

    # -------------------------------------------------------------------------
    def __init__(self, global_config, configurator):
        """Constructor method."""
        settings = configurator.registry.settings
        self.configurator = configurator
        self.is_front = bool(settings.get('storage.root'))
        self.is_agent = bool(settings.get('build.root'))
        self._config = ConfigParser({'here': global_config['here']})
        self._config.read(global_config['__file__'])
        self._lang = settings.get('pyramid.default_locale_name')
        mimetypes.init((join(dirname(__file__), 'Static', 'Images',
            'MimeTypes', 'mime.types'),))

    # -------------------------------------------------------------------------
    def all(self):
        """Check settings and create registry objects."""
        # Check general settings
        if not self.is_front and not self.is_agent:
            sys.exit('*** Must be at least a web site ("storage.root" '
                     'needed) or an agent ("build.root" needed).')
        settings = self.configurator.registry.settings
        if not self._lang or not settings.get('available_languages'):
            sys.exit('*** Must define available languages and a default one.')
        if not settings.get('uid'):
            sys.exit('*** Must define an "uid".')

        # Translations
        self.configurator.add_translation_dirs(
            *(settings.get('translation_dirs', '').split()
              + ['publiforge:Locale', 'colander:locale']))

        # Initialize agent
        if self.is_agent:
            self.configurator.registry['abuild'] = AgentBuildManager(settings)
            if len(self.configurator.registry['abuild'].processor_list()) == 0:
                sys.exit('*** Should have defined at least one processor.')
            fronts = self.configurator.registry['abuild'].front_list()
            if len(fronts) == 0:
                sys.exit('*** Must have at least one authorized front.')
            if not settings.get('buildspace.root') \
                   and (len(fronts) > 1 or fronts[0] != settings.get('uid')):
                sys.exit('*** Must define a directory for buildspaces.')
            self.configurator.include(add_routes_agent)

        # Initialize front
        if self.is_front:
            if not settings.get('temporary_dir'):
                sys.exit('*** Must define a temporary directory.')
            if exists(settings['temporary_dir']):
                rmtree(settings['temporary_dir'])
            makedirs(settings['temporary_dir'])
            cache_manager = CacheManager(
                **parse_cache_config_options(settings))
            self.configurator.registry['handler'] = HandlerManager(
                settings, cache_manager)
            if len(self.configurator.registry['handler'].vcs_list()) == 0:
                sys.exit('*** Should have defined at least one VCS.')
            self.configurator.registry['fbuild'] = FrontBuildManager(settings)
            if len(self.configurator.registry['fbuild'].agent_list()) == 0:
                sys.exit('*** Should have at least one available agent.')
            self.configurator.set_session_factory(
                session_factory_from_settings(settings))
            self.configurator.add_subscriber(new_request, NewRequest)
            self.configurator.add_subscriber(before_render, BeforeRender)
            self.configurator.set_default_permission('view')
            self.configurator.include(add_routes_front)
            self.configurator.scan()
            self.skin()
            self.initialize_sql()

        return self.is_front, self.is_agent

    # -------------------------------------------------------------------------
    def skin(self):
        """Set up skin."""
        settings = self.configurator.registry.settings
        if settings.get('skin.static.name'):
            if not settings.get('skin.static.path'):
                sys.exit('*** Must difine a static path.')
            self.configurator.add_static_view(
                settings['skin.static.name'], settings['skin.static.path'],
                cache_max_age=3600)
        if settings.get('skin.static.name') != 'Static':
            self.configurator.add_static_view('Static',
                join(dirname(__file__), 'Static'), cache_max_age=3600)

    # -------------------------------------------------------------------------
    def initialize_sql(self):
        """Database initialization."""
        # Initialize SqlAlchemy session
        settings = self.configurator.registry.settings
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        # Check database and empty processor table
        try:
            DBSession.query(Processor).delete()
            DBSession.commit()
        except ProgrammingError:
            sys.exit('*** Run "pfpopulate" script!')
        DBSession.close()


# =============================================================================
def perm_group_finder(user_id, request):
    """Return permission groups of user ``user_id``.

    :param user_id: (string)
        User ID.
    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    """
    # Already authenticated
    if user_id == request.session.get('user_id'):
        return ['group:%s' % perm for perm in request.session['perms']]

    # Auto login
    # pylint: disable = I0011, E1103
    user = connect(request, user_id)
    if not isinstance(user, int):
        user.setup_environment(request)
        return ['group:%s' % perm for perm in request.session['perms']]


# =============================================================================
class RootFactory(object):
    """Return the traversal root of the application.

    Its main role is to define Access Control List (ACL). See
    :ref:`frontreference_permissions` for a complete description of
    permissions.
    """
    # pylint: disable = I0011, R0903

    __acl__ = [
        (Allow, Authenticated, 'view'),
        (Allow, 'group:admin', ALL_PERMISSIONS),
        (Allow, 'group:doc_editor', 'doc.update'),
        (Allow, 'group:doc_manager', ('doc.update', 'doc.create')),
        (Allow, 'group:usr_user', 'usr.read'),
        (Allow, 'group:usr_editor', ('usr.read', 'usr.update')),
        (Allow, 'group:usr_manager', ('usr.read', 'usr.update', 'usr.create')),
        (Allow, 'group:grp_user', 'grp.read'),
        (Allow, 'group:grp_editor', ('grp.read', 'grp.update')),
        (Allow, 'group:grp_manager', ('grp.read', 'grp.update', 'grp.create')),
        (Allow, 'group:stg_user', 'stg.read'),
        (Allow, 'group:stg_editor', ('stg.read', 'stg.update')),
        (Allow, 'group:stg_manager', ('stg.read', 'stg.update', 'stg.create')),
        (Allow, 'group:prj_user', 'prj.read'),
        (Allow, 'group:prj_editor', ('prj.read', 'prj.update')),
        (Allow, 'group:prj_manager', ('prj.read', 'prj.update', 'prj.create')),
        ]

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        pass


# =============================================================================
def new_request(event):
    """A subscriber for :class:`pyramid.events.NewRequest` events."""
    request = event.request
    if not 'lang' in request.session:
        request.session['lang'] = request.accept_language.best_match(
            request.registry.settings.get('available_languages').split(),
            request.registry.settings.get('pyramid.default_locale_name'))
    request._LOCALE_ = request.session['lang']
    request.breadcrumbs = Breadcrumbs(request)


# =============================================================================
def before_render(event):
    """A subscriber for :class:`pyramid.events.BeforeRender` events."""
    # pylint: disable = I0011, W0142
    request = event.get('request') or get_current_request()

    def translate(text, domain='publiforge', **kwargs):
        """Translation from a string."""
        return get_localizer(request).translate(_(text, domain, **kwargs))

    event['base'] = get_renderer(
        request.registry.settings.get('skin.template.base')
        or 'Templates/base.pt').implementation()
    event['title'] = request.registry.settings.get(
        'skin.title', 'PubliForge').decode('utf8')
    event['_'] = translate
    event['route'] = lambda name, *elts, **kwargs: \
        request.route_path(name, *elts, **kwargs).decode('utf8')
    event['Menu'] = Menu


# =============================================================================
def add_routes_front(config):
    """Add Web front routes."""
    # pylint: disable = I0011, R0915
    # Security
    config.add_route('login', '/login')
    config.add_route('login_test', '/login_test')
    config.add_route('logout', '/logout')
    config.add_view('.views.security.login', route_name='login',
        renderer=config.registry.settings.get('skin.template.login')
            or 'Templates/login.pt',
        permission=NO_PERMISSION_REQUIRED)

    # Home
    config.add_route('home', '/')
    config.add_route('favicon', '/favicon.ico')
    config.add_route('robots', '/robots.txt')

    # Site
    config.add_route('site_admin', '/site/admin')

    # User
    config.add_route('user_account', '/user/account')
    config.add_route('user_admin', '/user/admin')
    config.add_route('user_create', '/user/create')
    config.add_route('user_view', '/user/view/{user_id}')
    config.add_route('user_edit', '/user/edit/{user_id}')

    # Group
    config.add_route('group_admin', '/group/admin')
    config.add_route('group_create', '/group/create')
    config.add_route('group_view', '/group/view/{group_id}')
    config.add_route('group_edit', '/group/edit/{group_id}')

    # Storage
    config.add_route('storage_admin', '/storage/admin')
    config.add_route('storage_index', '/storage/index')
    config.add_route('storage_index_ajax', '/storage/index_ajax')
    config.add_route('storage_create', '/storage/create')
    config.add_route('storage_view', '/storage/view/{storage_id}')
    config.add_route('storage_edit', '/storage/edit/{storage_id}')
    config.add_route('storage_root', '/storage/browse/{storage_id}')
    config.add_route('storage_browse',
                     '/storage/browse/{storage_id}/*path')
    config.add_route('storage_root_ajax',
                     '/storage/browse_ajax/{storage_id}')
    config.add_route('storage_browse_ajax',
                     '/storage/browse_ajax/{storage_id}/*path')

    # File
    config.add_route('file_search', '/file/search')
    config.add_route('file_info', '/file/info/{storage_id}/*path')
    config.add_route('file_download', '/file/download/{storage_id}/*path')
    config.add_route('file_revision',
                     '/file/revision/{revision}/{storage_id}/*path')
    config.add_route('file_diff', '/file/diff/{revision}/{storage_id}/*path')

    # Project
    config.add_route('project_admin', '/project/admin')
    config.add_route('project_index', '/project/index')
    config.add_route('project_create', '/project/create')
    config.add_route('project_view', '/project/view/{project_id}')
    config.add_route('project_edit', '/project/edit/{project_id}')
    config.add_route('project_dashboard', '/project/dashboard/{project_id}')
    config.add_route('project_results', '/project/results/{project_id}')
    config.add_route('project_results_ajax',
                     '/project/results_ajax/{project_id}')

    # Processing
    config.add_route('processing_create', '/processing/create/{project_id}')
    config.add_route('processing_view',
                     '/processing/view/{project_id}-{processing_id}')
    config.add_route('processing_edit',
                     '/processing/edit/{project_id}-{processing_id}')

    # Pack
    config.add_route('pack_create', '/pack/create/{project_id}')
    config.add_route('pack_view', '/pack/view/{project_id}-{pack_id}')
    config.add_route('pack_edit', '/pack/edit/{project_id}-{pack_id}')

    # Build
    config.add_route('build_launch',
                     '/build/launch/{project_id}-{processing_id}-{pack_ids}')
    config.add_route('build_view', '/build/view/{build_id}')
    config.add_route('build_progress', '/build/progress/{build_id}')
    config.add_route('build_progress_ajax', '/build/progress_ajax/{build_id}')
    config.add_route('build_complete', '/build/complete/{build_id}/{key}')
    config.add_route('build_log', '/build/log/{build_id}')


# =============================================================================
def add_routes_agent(config):
    """Add agent routes and methods."""
    config.include('pyramid_rpc.xmlrpc')
    config.add_xmlrpc_endpoint('xmlrpc', '/xmlrpc')

    config.add_xmlrpc_method('.views.xmlrpc.processor_list',
        endpoint='xmlrpc', method='processor_list',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.processor_xml',
        endpoint='xmlrpc', method='processor_xml',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method(
        '.views.xmlrpc.activity', endpoint='xmlrpc', method='activity',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method(
        '.views.xmlrpc.start', endpoint='xmlrpc', method='start',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method(
        '.views.xmlrpc.progress', endpoint='xmlrpc', method='progress',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method(
        '.views.xmlrpc.stop', endpoint='xmlrpc', method='stop',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method(
        '.views.xmlrpc.result', endpoint='xmlrpc', method='result',
        permission=NO_PERMISSION_REQUIRED)

    config.add_xmlrpc_method('.views.xmlrpc.buildspace_cleanup',
        endpoint='xmlrpc', method='buildspace_cleanup',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.buildspace_send_signature',
        endpoint='xmlrpc', method='buildspace_send_signature',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.buildspace_receive_file',
        endpoint='xmlrpc', method='buildspace_receive_file',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.buildspace_receive_delta',
        endpoint='xmlrpc', method='buildspace_receive_delta',
        permission=NO_PERMISSION_REQUIRED)

    config.add_xmlrpc_method('.views.xmlrpc.output_list',
        endpoint='xmlrpc', method='output_list',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.output_send_file',
        endpoint='xmlrpc', method='output_send_file',
        permission=NO_PERMISSION_REQUIRED)
    config.add_xmlrpc_method('.views.xmlrpc.output_send_delta',
        endpoint='xmlrpc', method='output_send_delta',
        permission=NO_PERMISSION_REQUIRED)
