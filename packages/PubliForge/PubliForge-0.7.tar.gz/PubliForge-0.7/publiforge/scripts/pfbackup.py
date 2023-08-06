#!/usr/bin/env python
# $Id: pfbackup.py 8e0eacb6ec37 2012/08/05 17:55:59 patrick $
"""Backup site into a XML file."""

import sys
import logging
from os import getcwd
from os.path import exists, basename
from optparse import OptionParser
from locale import getdefaultlocale
from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.threadlocal import get_current_registry

from ..lib.utils import _, localizer
from ..lib.xml import export_configuration
from ..lib.build.agent import AgentBuildManager
from ..lib.build.front import FrontBuildManager
from ..models import DBSession, Base
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.projects import Project


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = OptionParser(
        'Usage: %prog <config_uri> <backup_file>\n'
        'Examples:\n  %prog production.ini pfinstance.pf.xml'
        '\n  %prog production.ini#Foo pfinstance.pf.xml --nousers')
    parser.add_option(
        '--nousers', dest='nousers',
        help='no backup for users', default=False, action='store_true')
    parser.add_option(
        '--nogroups', dest='nogroups',
        help='no backup for groups', default=False, action='store_true')
    parser.add_option(
        '--nostorages', dest='nostorages',
        help='no backup for storages', default=False, action='store_true')
    parser.add_option(
        '--noprojects', dest='noprojects',
        help='no backup for projects', default=False, action='store_true')
    parser.add_option(
        '--loglevel', dest='log_level', help='log level', default='INFO')
    opts, args = parser.parse_args()
    log_level = getattr(logging, opts.log_level.upper(), None)
    if len(args) < 2 or not exists(args[0].partition('#')[0]) or not log_level:
        parser.error('Incorrect argument')
        sys.exit(2)

    logformat = '%(levelname)-8s %(message)s'
    logging.basicConfig(level=log_level, format=logformat)
    Backup(opts).save(args[0], args[1])


# =============================================================================
class Backup(object):
    """Class to backup site."""

    # -------------------------------------------------------------------------
    def __init__(self, opts):
        """Constructor method."""
        self._opts = opts

    # -------------------------------------------------------------------------
    def save(self, conf_uri, filename):
        """Save asked elements.

        :param conf_uri: (string)
            Configuration file of the instance.
        :param filename: (string)
            Name of backup file.
        :return: (boolean)
        """
        # Read configuration file
        settings = get_appsettings(conf_uri)
        if 3 > len(settings):
            try:
                settings = get_appsettings(conf_uri, 'PubliForge')
            except LookupError:
                settings = get_appsettings(conf_uri, basename(getcwd()))
        if 'uid' not in settings or 'sqlalchemy.url' not in settings:
            LOG.error(localizer(getdefaultlocale()[0]).translate(_(
                'Unable to read configuration file "${f}".', {'f': conf_uri})))
            return False

        # Initialize SqlAlchemy session
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        # Browse elements
        elements = self._get_elements(settings)

        # Export configuration
        if elements:
            export_configuration(elements, filename, True)
        else:
            LOG.warning(localizer(
                getdefaultlocale()[0]).translate(_('nothing to do!')))
        DBSession.close()
        DBSession.remove()
        return True

    # -------------------------------------------------------------------------
    def _get_elements(self, settings):
        """Get all XML elements of the configuration.

        :param settings: (dictionary)
            Settings dictionary.
        :return: (list)
        """
        elements = []

        if not hasattr(self._opts, 'nousers') or not self._opts.nousers:
            for user in DBSession.query(User):
                elements.append(user.xml(True))

        if not hasattr(self._opts, 'nogroups') or not self._opts.nogroups:
            for group in DBSession.query(Group):
                elements.append(group.xml())

        if not hasattr(self._opts, 'nostorages') or not self._opts.nostorages:
            for storage in DBSession.query(Storage):
                elements.append(storage.xml())

        if not hasattr(self._opts, 'noprojects') or not self._opts.noprojects:
            request = DummyRequest(settings)
            for project in DBSession.query(Project):
                elements.append(project.xml(request))

        return elements


# =============================================================================
class DummyRequest(object):
    """Dummy request for processors."""
    # pylint: disable = I0011, R0903

    # -------------------------------------------------------------------------
    def __init__(self, settings):
        """Constructor method."""
        self.registry = get_current_registry()
        self.registry['abuild'] = AgentBuildManager(settings)
        self.registry['fbuild'] = FrontBuildManager(settings)
        self.registry.settings = settings
        self.session = {'lang': getdefaultlocale()[0], 'user_id': 1}
