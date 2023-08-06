# $Id: none.py 513105aef084 2012/02/13 16:15:59 patrick $
"""Storage with no Version Control System management."""

from os import makedirs, remove, renames
from os.path import exists, isfile, getmtime
from shutil import rmtree
from datetime import datetime

from pyramid.i18n import TranslationString

from ...lib.utils import _
from ...lib.vcs import Vcs


# =============================================================================
class VcsNone(Vcs):
    """No Version Control System."""

    engine = 'none'

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        if not exists(self.path):
            makedirs(self.path)

    # -------------------------------------------------------------------------
    def pull_update(self, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.pull_update`.
        """
        pass

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.commit_push`.
        """
        pass

    # -------------------------------------------------------------------------
    def revert_all(self, handler):
        """Revert all files of the repository."""
        pass

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        return datetime.fromtimestamp(getmtime(self.path)), '-', '-'

    # -------------------------------------------------------------------------
    def file_infos(self, path, filename):
        """Return information on a file.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        return (datetime.fromtimestamp(
            getmtime(self.full_path(path, filename))), '-', '-', '-')

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.lib.vcs.Vcs.log`.
        """
        return ((datetime.fromtimestamp(
            getmtime(self.full_path(path, filename))), '-', '-', '-'),)

    # -------------------------------------------------------------------------
    def add(self, path, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.add`.
        """
        pass

    # -------------------------------------------------------------------------
    def rename(self, path, filename, new_name, handler):
        """Rename a file."""
        new_name = self.full_path(path, new_name)
        if isinstance(new_name, TranslationString):
            return handler.report('error', new_name)
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if exists(new_name):
            return handler.report('error', _('File already exists!'))
        try:
            renames(filename, new_name)
        except OSError, error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def remove(self, path, filename, handler):
        """Remove a file.

        See :meth:`~.lib.vcs.Vcs.remove`.
        """
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if exists(filename):
            if isfile(filename):
                remove(filename)
            else:
                rmtree(filename)

    # -------------------------------------------------------------------------
    def revision(self, fullname, revision):
        """Retrieve a revision.

        See :meth:`~.lib.vcs.Vcs.revision`.
        """
        with open(fullname, 'rb') as hdl:
            content = hdl.read()
        return content

    # -------------------------------------------------------------------------
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision.

        See :meth:`~.lib.vcs.Vcs.diff`.
        """
        return ''
