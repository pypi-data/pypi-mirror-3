#!/usr/bin/env python
# $Id: pfbackup.py 172137ab6744 2012/02/23 22:55:35 patrick $
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


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = OptionParser('Usage: %prog <config_uri> <backup_file>\n'
        'Examples:\n  %prog production.ini pfinstance.pf.xml'
        '\n  %prog production.ini#Foo pfinstance.pf.xml --nousers')
    parser.add_option('--nousers', dest='nousers',
        help='no backup for users', default=False, action='store_true')
    parser.add_option('--nogroups', dest='nogroups',
        help='no backup for groups', default=False, action='store_true')
    parser.add_option('--nostorages', dest='nostorages',
        help='no backup for storages', default=False, action='store_true')
    parser.add_option('--noprojects', dest='noprojects',
        help='no backup for projects', default=False, action='store_true')
    parser.add_option('--loglevel', dest='log_level', help='log level',
        default='INFO')
    opts, args = parser.parse_args()
    log_level = getattr(logging, opts.log_level.upper(), None)
    if len(args) < 2 or not exists(args[0].partition('#')[0]) or not log_level:
        parser.error('Incorrect argument')
        sys.exit(2)

    logformat = '%(levelname)-8s %(message)s'
    logging.basicConfig(level=log_level, format=logformat)
    Backup(args[0]).save(opts, args[1])


# =============================================================================
class Backup(object):
    """Class to backup site."""

    # -------------------------------------------------------------------------
    def __init__(self, conf_uri):
        """Constructor method."""
        self._settings = get_appsettings(conf_uri)
        if 3 > len(self._settings):
            try:
                self._settings = get_appsettings(conf_uri, 'PubliForge')
            except LookupError:
                self._settings = get_appsettings(conf_uri, basename(getcwd()))

    # -------------------------------------------------------------------------
    def save(self, opts, filename):
        """Save asked elements.

        :param opts: (dictionary)
            List of command line options.
        :param filename: (string)
            Name of backup file.
        """
        # Initialize SqlAlchemy session
        engine = engine_from_config(self._settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

        # Browse elements
        elements = []
        if not opts.nousers:
            for user in DBSession.query(User):
                elements.append(user.xml(True))
        if not opts.nogroups:
            for group in DBSession.query(Group):
                elements.append(group.xml())
        if not opts.nostorages:
            for storage in DBSession.query(Storage):
                elements.append(storage.xml())
        if not opts.noprojects:
            request = DummyRequest(self._settings)
            for project in DBSession.query(Project):
                elements.append(project.xml(request))

        # Export configuration
        if elements:
            export_configuration(elements, filename, True)
        else:
            logging.warning(localizer(
                getdefaultlocale()[0]).translate(_('nothing to do!')))
        DBSession.close()


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
