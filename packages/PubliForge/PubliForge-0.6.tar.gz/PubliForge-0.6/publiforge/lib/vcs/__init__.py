# $Id: __init__.py 9a2faf8ae708 2012/02/21 10:45:50 patrick $
"""Version Control System library."""

from abc import ABCMeta, abstractmethod
from os import mkdir, remove
from os.path import exists, join, normpath
from locale import resetlocale
from datetime import datetime
from urlparse import urlparse, urlunparse

from pyramid.i18n import TranslationString

from ...lib.utils import _, EXCLUDED_FILES


# =============================================================================
class Vcs(object):
    """Abstract base class for version control class."""

    __metaclass__ = ABCMeta
    engine = None

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method.

        :param path: (string)
             Path to local copy.
        :param url: (string)
            URL of source repository.
        :param user_id: (string, optional)
            User ID for clone/pull access.
        :param password: (string, optional)
            Password for clone/pull access.
        """
        resetlocale()
        self.path = str(normpath(path))
        self.url = str(url)
        self._user_id = str(user_id or '')
        self._password = str(password or '')

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<Vcs('%s', '%s', '%s', '%s')>" % (
            self.engine, self.path, self.url, self._user_id)

    # -------------------------------------------------------------------------
    @abstractmethod
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance, optional)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def pull_update(self, handler):
        """Pull changes and update. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes. (abstract)

        :param message: (string)
            Commit message.
        :param user_id: (string)
            User ID for VCS access.
        :param password: (string)
            Cleared password for VCS access.
        :param name: (string)
            Name for VCS access.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def revert_all(self, handler):
        """Revert all files of the repository. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def last_change(self):
        """Return the last change on the repository. (abstract)

        :return: (tuple)
           A tuple such as ``(date, changeset, user)``.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def file_infos(self, path, filename):
        """Return information on a file. (abstract)

        :param path: (string)
            Relative path.
        :param filename: (string)
            Name of the file to read.
        :return: (tuple)
            A tuple such as ``(date, changeset, user, message)``.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        :param path: (string)
            Relative path to file.
        :param filename: (string)
            Name of the file.
        :param limit: (integer, default=1)
            Maximum number of entries in log.
        :return: (list of tuples or string)
            Log or error message.

        Each tuple or entry is like ``(date, changeset, user, message)``.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def add(self, path, handler):
        """Add all new files in ``path``. (abstract)

        :param path: (string)
            Relative path to browse.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    def mkdir(self, path, name, handler):
        """Make the directroy ``name``.

        :param path: (string)
            Relative path to directory to create.
        :param name: (string)
            Name of directory to create.
        """
        name = self.full_path(path, name)
        if isinstance(name, TranslationString):
            return handler.report('error', name)
        if not exists(name):
            mkdir(name)

    # -------------------------------------------------------------------------
    @abstractmethod
    def rename(self, path, filename, new_name, handler):
        """Rename a file. (abstract)

        :param path: (string)
            Relative path to file to rename.
        :param filename: (string)
            Name of the file to remove.
        :param new_new: (string)
            New name.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def remove(self, path, filename, handler):
        """Remove a file. (abstract)

        :param path: (string)
            Relative path to file to remove.
        :param filename: (string)
            Name of the file to remove.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def revision(self, fullname, revision):
        """Retrieve a revision. (abstract)

        :param fullname: (string)
            Full name of the file.
        :param revision: (string)
            Revision number to retrieve.
        :return: (string)
            Content of the file.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision. (abstract)

        :param fullname: (string)
            Full name of the file.
        :param revision: (string)
            Revision number to compare.
        :return: (string)
            Differences.
        """
        pass

    # -------------------------------------------------------------------------
    def full_path(self, *path):
        """Return normalized full path of ``path`` file or an error message if
        it is outside the storage.

        :param path: (strings)
            Path chunks.
        :return: (string or :class:`pyramid.i18n.TranslationString` instance)
            Full path or error message.
        """
        full_path = normpath(join(self.path, *path))
        if not full_path.startswith(self.path):
            full_path = self.path
        return full_path.encode('utf8')

    # -------------------------------------------------------------------------
    def _log_path(self, path, filename):
        """Return normalized full path of file or ``None``.

        :param path: (string)
            Relative path to file.
        :param filename: (string)
            Name of file.
        :return: (string or ``None``)
            Normalized full path or ``None`` if the file is not eligible.
        """
        if filename in EXCLUDED_FILES:
            return
        filename = normpath(join(self.path, path, filename))
        if not filename.startswith(self.path) or not exists(filename):
            return
        return filename.encode('utf8')

    # -------------------------------------------------------------------------
    def _full_url(self, user_id=None, password=None):
        """Return an URL with user_id and password.

        :param user_id: (string)
            User ID for VCS access.
        :param password: (string)
            Password ID for VCS access.
        :return: (string)
            Full URL.
        """
        user_id = user_id or self._user_id
        if not user_id:
            return self.url
        scheme, netloc, path, params, query, fragment = urlparse(str(self.url))
        netloc = '%s:%s@%s' % (user_id, password or self._password,
                               netloc.rpartition('@')[2])
        return urlunparse((scheme, netloc, path, params, query, fragment))
