# $Id: svn.py f6a06566f45f 2012/07/31 22:58:36 patrick $
"""Storage with Subversion Version Control System management."""

import logging
from os import remove, listdir
from os.path import exists, getmtime, join, isdir, relpath
from shutil import rmtree
from datetime import datetime
from cStringIO import StringIO
from urllib import quote
from time import sleep

from subvertpy import SubversionException, ra, client
from subvertpy import AUTH_PARAM_DEFAULT_USERNAME, AUTH_PARAM_DEFAULT_PASSWORD
from subvertpy.ra import BusyException
from subvertpy.properties import PROP_REVISION_LOG, PROP_REVISION_AUTHOR
from subvertpy.properties import PROP_REVISION_DATE, time_from_cstring

from pyramid.i18n import TranslationString

from ...lib.utils import _, execute
from ...lib.vcs import Vcs


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsSubversion(Vcs):
    """Version control system with Subversion."""

    engine = 'svn'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        super(VcsSubversion, self).__init__(path, url, user_id, password)
        providers = ra.get_platform_specific_client_providers()
        providers += [
            ra.get_ssl_client_cert_file_provider(),
            ra.get_ssl_client_cert_pw_file_provider(),
            ra.get_ssl_server_trust_prompt_provider(self._get_server_trust),
            ra.get_username_prompt_provider(self._get_user, 0),
            ra.get_simple_prompt_provider(self._get_pass, 0)]

        self._auth = ra.Auth(providers)
        if self._user_id:
            self._auth.set_parameter(
                AUTH_PARAM_DEFAULT_USERNAME, self._user_id)
        if self._password:
            self._auth.set_parameter(
                AUTH_PARAM_DEFAULT_PASSWORD, self._password)

        self._client = client.Client(auth=self._auth)
        self._remote = None
        self._counter = 0

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        try:
            self._client.checkout(self.url, self.path, 'HEAD')
        except (OSError, SubversionException), error:
            if handler is not None:
                handler.report('error', error[0].decode('utf8'))
            return error[0].decode('utf8')

    # -------------------------------------------------------------------------
    def pull_update(self, handler):
        """Pull changes and update.

        See abstract function :meth:`~.lib.vcs.Vcs.pull_update`.
        """
        if not exists(self.path):
            return
        try:
            self._client.update(self.path)
        except SubversionException, error:
            return handler.report(
                'error', error[0].replace(self.path, '').decode('utf8'))

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes.

        See abstract method :meth:`~.lib.vcs.Vcs.commit_push`.
        """
        if not exists(self.path):
            return

        cmd = ['nice', 'svn', '-q', '--non-interactive', '--no-auth-cache']
        if user_id:
            cmd += ['--username', user_id]
        if password:
            cmd += ['--password', password]
        cmd += ['commit', '-m', message]
        error = execute(cmd, self.path)
        if error:
            error = error[0] or error[1]
            return handler.report('error', error.replace(self.path, ''))

    # -------------------------------------------------------------------------
    def revert_all(self, handler):
        """Revert all files of the repository."""
        if not exists(self.path):
            return
        cmd = ['nice', 'svn', '-q', '--non-interactive', '--no-auth-cache',
               'revert', '--recursive', '.']
        execute(cmd, self.path)
        try:
            self._client.update(self.path)
        except SubversionException:
            pass

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        try:
            self._set_remote()
            stat = self._remote.stat('.', self._remote.get_latest_revnum())
            return (
                datetime.fromtimestamp(long(stat['time']) / 1000000),
                stat['created_rev'], stat['last_author'])
        except (SubversionException, ValueError, BusyException):
            return datetime.fromtimestamp(getmtime(self.path)), '-', '-'

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.lib.vcs.Vcs.log`.
        """
        _log = []
        relname = join(path, filename).encode('utf8')

        def _log_printer(changed_paths, rev, revprops, has_children=None):
            """Catch log information."""
            # pylint: disable = I0011, W0613
            info = dict(revprops.items())
            _log.append((
                datetime.fromtimestamp(
                    (time_from_cstring(info[PROP_REVISION_DATE])) / 1000000),
                rev, info[PROP_REVISION_AUTHOR].decode('utf8'),
                info[PROP_REVISION_LOG].decode('utf8')))

        try:
            self._set_remote()
            self._remote.get_log(
                _log_printer, paths=relname,
                start=self._remote.get_latest_revnum(), end=0, limit=limit)
        except BusyException:
            if self._counter < 10:
                sleep(1)
                self._counter += 1
                return self.log(path, filename, limit)
            self._counter = 0
            return ((datetime.fromtimestamp(
                getmtime(self.full_path(path, filename))), '-', '-', '-'),)
        except SubversionException:
            self._counter = 0
            return ((datetime.fromtimestamp(
                getmtime(self.full_path(path, filename))), '-', '-', '-'),)

        self._counter = 0
        return _log

    # -------------------------------------------------------------------------
    def add(self, path, handler):
        """Add all new files in ``path``.

        See abstract function :meth:`~.lib.vcs.Vcs.add`.
        """
        fullpath = self.full_path(path)
        if isinstance(fullpath, TranslationString):
            return handler.report('error', fullpath)

        for name in listdir(fullpath):
            if name != '.svn':
                try:
                    self._client.add(join(fullpath, name).encode('utf8'))
                except SubversionException:
                    pass

    # -------------------------------------------------------------------------
    def mkdir(self, path, name, handler):
        """Make the directroy ``name``.

        See abstract function :meth:`~.lib.vcs.Vcs.mkdir`.
        """
        fullname = self.full_path(path, name)
        if isinstance(fullname, TranslationString):
            return handler.report('error', fullname)
        if not exists(fullname):
            try:
                self._client.mkdir(fullname)
            except SubversionException, error:
                return handler.report(
                    'error', error[0].replace(self.path, '').decode('utf8'))

    # -------------------------------------------------------------------------
    def rename(self, path, filename, new_name, handler):
        """Rename a file."""
        fullname = self.full_path(path, filename)
        if isinstance(fullname, TranslationString):
            return handler.report('error', fullname)
        new_fullname = self.full_path(path, new_name)
        if isinstance(new_fullname, TranslationString):
            return handler.report('error', new_fullname)
        if exists(new_fullname):
            return handler.report('error', _('File already exists!'))
        try:
            self._client.copy(fullname, new_fullname)
            self._client.delete(fullname)
        except SubversionException, error:
            return handler.report(
                'error', error[0].replace(self.path, '').decode('utf8'))

    # -------------------------------------------------------------------------
    def remove(self, path, filename, handler):
        """Remove a file.

        See abstract function :meth:`~.lib.vcs.Vcs.remove`.
        """
        fullname = self.full_path(path, filename)
        if isinstance(fullname, TranslationString):
            return handler.report('error', fullname)
        if exists(fullname):
            try:
                self._client.delete(fullname)
            except SubversionException, error:
                if isdir(fullname):
                    rmtree(fullname)
                elif exists(fullname):
                    remove(fullname)
                return handler.report(
                    'error', error[0].replace(self.path, '').decode('utf8'))

    # -------------------------------------------------------------------------
    def revision(self, fullname, revision):
        """Retrieve a revision.

        See :meth:`~.lib.vcs.Vcs.revision`.
        """
        out = StringIO()
        relname = relpath(fullname, self.path)
        try:
            self._set_remote()
            self._remote.get_file(relname, out, int(revision))
        except SubversionException, error:
            return error[0].replace(self.path, '').decode('utf8')

        content = out.getvalue()
        out.close()
        return content

    # -------------------------------------------------------------------------
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision.

        See :meth:`~.lib.vcs.Vcs.diff`.
        """
        relname = relpath(fullname, self.path)
        try:
            self._set_remote()
            stat = self._remote.stat(relname, self._remote.get_latest_revnum())
        except SubversionException, error:
            return error[0].replace(self.path, '').decode('utf8')

        url = self._path2url(relname)
        try:
            out, err = self._client.diff(
                int(revision), int(stat['created_rev']), url, url)
        except SubversionException, error:
            return error[0].replace(self.path, '').decode('utf8')
        error = err.read()
        diff = out.read()
        err.close()
        out.close()
        if error:
            return error.replace(self.path, '').decode('utf8')
        return diff.decode('utf8')

    # -------------------------------------------------------------------------
    def _set_remote(self):
        """Set the Subversion remote access."""
        if self._remote is not None:
            return
        self._remote = ra.RemoteAccess(
            url=self.url, client_string_func=self._get_client_string,
            auth=self._auth)

    # -------------------------------------------------------------------------
    @classmethod
    def _get_client_string(cls):
        """Return a client identification string."""
        return 'publiforge'

    # -------------------------------------------------------------------------
    def _get_user(self, realm, may_save):
        """Call back function called to get a user name to access a
        repository.
        """
        # pylint: disable = I0011, W0613
        return self._user_id, False

    # -------------------------------------------------------------------------
    def _get_pass(self, realm, username, may_save):
        """Call back function called to get a user name an password to access a
        repository.
        """
        # pylint: disable = I0011, W0613
        return self._user_id or username, self._password, False

    # -------------------------------------------------------------------------
    @classmethod
    def _get_server_trust(cls, url, retry, certificate, may_save):
        """Call back function called to trust server."""
        # pylint: disable = I0011, W0613
        return True, False

    # -------------------------------------------------------------------------
    def _path2url(self, path):
        """Build svn URL for path, URL-escaping path."""
        if not path or path == '.':
            return self.url
        assert path[0] != '/', path
        return '/'.join((self.url, quote(path).rstrip('/'),))
