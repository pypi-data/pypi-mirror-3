#!/usr/bin/env python
# $Id: pfpopulate.py e0c34b8eafc9 2012/09/01 10:36:44 patrick $
"""Populate database and storages."""

import sys
import logging
from os import listdir, getcwd, remove
from os.path import exists, join, basename, isdir
from shutil import rmtree
from optparse import OptionParser
from ConfigParser import ConfigParser
from locale import getdefaultlocale
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from sqlalchemy import engine_from_config
from sqlalchemy.exc import OperationalError

from pyramid.paster import get_appsettings

from ..lib.utils import _, localizer, config_get, normalize_name
from ..lib.xml import import_configuration
from ..lib.handler import HandlerManager
from ..models import ID_LEN, DBSession, Base
from ..models.users import PAGE_SIZE, User, UserPerm, UserIP
from ..models.storages import Storage


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = OptionParser(
        'Usage: %prog <config_uri> [<file> <file>...]\n'
        'Examples:\n  %prog production.ini\n'
        '  %prog development.ini users.pfu.xml\n'
        '  %prog production.ini#Foo')
    parser.add_option(
        '--drop_tables', dest='drop_tables',
        help='drop existing tables', default=False, action='store_true')
    parser.add_option(
        '--no_pull', dest='no_pull',
        help='do not synchronize storages', default=False, action='store_true')
    parser.add_option(
        '--loglevel', dest='log_level', help='log level', default='INFO')
    opts, args = parser.parse_args()
    log_level = getattr(logging, opts.log_level.upper(), None)
    if not log_level or len(args) < 1 or not exists(args[0].partition('#')[0]):
        parser.error('Incorrect argument')
        sys.exit(2)

    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(level=log_level, format=logformat)
    Populate(opts, args[0]).all(args[1:])


# =============================================================================
class Populate(object):
    """Class to populate database and storages."""

    # -------------------------------------------------------------------------
    def __init__(self, opts, conf_uri):
        """Constructor method."""
        self._opts = opts
        self._settings = get_appsettings(conf_uri)
        if len(self._settings) < 3:
            try:
                self._settings = get_appsettings(conf_uri, 'PubliForge')
            except LookupError:
                self._settings = get_appsettings(conf_uri, basename(getcwd()))
        self._config = ConfigParser({'here': self._settings['here']})
        self._config.read(self._settings['__file__'])
        self._lang = self._settings.get('pyramid.default_locale_name')

    # -------------------------------------------------------------------------
    def all(self, files=list()):
        """Check settings, initialize database and create storages.

        :param files: (list, optional)
             List of files on command-line.
        :return: (boolean)
        """
        # Check general settings
        if not self._lang or not self._settings.get('languages'):
            LOG.error(self._translate(_(
                'Must define available languages and a default one.')))
            return False
        if not self._settings.get('uid'):
            LOG.error(self._translate(_(
                'Must define an unique identifier for this instance.')))
            return False

        # Clean build directory
        if exists(self._settings.get('build.root')):
            for name in listdir(self._settings['build.root']):
                name = join(self._settings['build.root'], name)
                if isdir(name):
                    rmtree(name)
                else:
                    remove(name)

        # Agent only
        if self._settings.get('storage.root') is None:
            return True

        # Populate
        if not self._initialize_sql():
            return False
        self._populate_admin()
        self._populate_from_xml(files)
        if DBSession.query(UserPerm)\
                .filter_by(scope='all', level='admin').first() is None:
            LOG.error(self._translate(_('You must define an administrator.')))
            DBSession.remove()
            return False
        self._update_storages()
        DBSession.remove()
        return True

    # -------------------------------------------------------------------------
    def _initialize_sql(self):
        """Database initialization.

        :return: (boolean)
            ``True`` if it succeeds.
        """
        # Initialize SqlAlchemy session
        engine = engine_from_config(self._settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        # Eventually, drop any existing tables
        if self._opts.drop_tables or bool(self._settings.get('drop_tables')):
            LOG.info(self._translate(_('###### Dropping existing tables')))
            try:
                Base.metadata.drop_all()
            except OperationalError, err:
                LOG.error(err[0])
                return

        # Create the tables if they don't already exist
        try:
            Base.metadata.create_all(engine)
        except OperationalError, err:
            LOG.error(err[0])
            return

        return True

    # -------------------------------------------------------------------------
    def _populate_admin(self):
        """Populate database with an administrator."""
        # pylint: disable = I0011, W0142
        if not self._config.has_option('Populate', 'admin.login'):
            return

        LOG.info(self._translate(_('###### Adding administrator')))
        login = normalize_name(self._get('admin.login'))[0:ID_LEN]
        ips = self._get('admin.ips', '')
        record = {
            'status': 'active',
            'password': self._get('admin.password'),
            'name': self._get('admin.name'),
            'email': self._get('admin.email'),
            'lang': self._get('admin.language', self._lang),
            'restrict_ip': bool(ips),
            'home': self._get('admin.home', 'site'),
            'page_size': int(self._get('admin.page_size', PAGE_SIZE))}
        if not record['password'] or not record['name']\
                or not record['email']:
            sys.exit('*** Incorrect administrator definition.')
        user = DBSession.query(User.login).filter_by(login=login).first()
        if user is not None:
            return
        user = User(self._settings, login, **record)
        DBSession.add(user)
        DBSession.commit()

        user.perms.append(UserPerm(user.user_id, 'all', 'admin'))
        for my_ip in ips.split():
            user.ips.append(UserIP(user.user_id, my_ip))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def _populate_from_xml(self, files):
        """Populate database with XML content.

        :param files: (list)
             List of files on command-line.
        """
        if not self._config.has_section('Populate') and not files:
            return
        LOG.info(self._translate(_('###### Loading configurations')))
        for idx in range(100):
            option = 'file.%d' % idx
            if not self._config.has_option('Populate', option):
                continue
            filename = self._get(option)
            LOG.info(filename)
            errors = import_configuration(
                self._settings, filename, error_if_exists=False)
            for error in errors:
                LOG.error(self._translate(error))

        for filename in files:
            LOG.info(filename)
            errors = import_configuration(
                self._settings, filename, error_if_exists=False)
            for error in errors:
                LOG.error(self._translate(error))

    # -------------------------------------------------------------------------
    def _update_storages(self):
        """Update all storages."""
        cache_manager = CacheManager(
            **parse_cache_config_options(self._settings))
        handler_manager = HandlerManager(self._settings, cache_manager)

        LOG.info(self._translate(_('###### Updating storages')))
        for storage in DBSession.query(Storage):
            storage_dir = join(
                self._settings['storage.root'], storage.storage_id)
            handler = handler_manager.get_handler(storage.storage_id, storage)
            if handler is None:
                LOG.error(self._translate(
                    _('${e}: unkwown engine', {'e': storage.vcs_engine})))
            elif not exists(storage_dir) or not listdir(storage_dir):
                LOG.info('{0:.<32}'.format(storage.storage_id))
                error = handler.clone()
                if error:
                    LOG.error(error)
            elif not hasattr(self._opts, 'no_pull') \
                    or not self._opts.no_pull:
                LOG.info('{0:.<32}'.format(storage.storage_id))
                handler.synchronize(None, True)

    # -------------------------------------------------------------------------
    def _get(self, option, default=None):
        """Retrieve a value from section [Populate].

        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, 'Populate', option, default)

    # -------------------------------------------------------------------------
    @classmethod
    def _translate(cls, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(getdefaultlocale()[0]).translate(text)
