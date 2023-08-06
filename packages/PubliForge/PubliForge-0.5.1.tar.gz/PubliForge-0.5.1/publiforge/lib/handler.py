# $Id: handler.py 513105aef084 2012/02/13 16:15:59 patrick $
"""A *handler* manages access to a storage.
"""

from os import listdir, walk
from os.path import join, getsize, splitext
from time import time, sleep
from threading import Thread
from locale import strxfrm

from .utils import _, decrypt, unzip, get_mime_type
from .utils import age, size_label, cache_method
from .vcs.none import VcsNone
from .vcs.hg import VcsMercurial, VcsLocal


# =============================================================================
class HandlerManager(object):
    """This class manages all handlers.

    One instance of :class:`HandlerManager` is created during application
    initialization. It is only used in front mode. It is stored in application
    registry.

    ``self.cache_manager`` is a :class:`beaker.cache.CacheManager` instance.

    ``self._handlers`` is a dictionary of :class:`Handler` objects.
    """

    # -------------------------------------------------------------------------
    def __init__(self, settings, cache_manager):
        """Constructor method.

        :param settings: (dictionary)
            Setting dictionary.
        :param cache_manager: (:class:`beaker.cache.CacheManager` instance)
            Global Beaker cache manager.
        """
        # Attributes
        self.settings = settings
        self.cache_manager = cache_manager
        self._handlers = {}

        # VCS engine classes
        vcs_classes = {'none': VcsNone, 'local': VcsLocal, 'hg': VcsMercurial}
        self.vcs_classes = {}
        for vcs in settings.get('storage.available_vcs', '').split():
            if vcs in vcs_classes and not vcs in self.vcs_classes:
                self.vcs_classes[vcs] = vcs_classes[vcs]

    # -------------------------------------------------------------------------
    def vcs_list(self):
        """Return a list of available Version Control System."""
        return self.vcs_classes.keys()

    # -------------------------------------------------------------------------
    def get_handler(self, storage_id, storage=None):
        """Create or retrieve a Storage Control System for storage
        ``storage``.

        :param storage_id: (string)
            Storage ID.
        :param storage: (:class:`~.models.storages.Storage` instance,
            optional).
        :return: (:class:`Handler` instance or ``None``)
        """
        self._cleanup()
        if storage_id in self._handlers:
            self._handlers[storage_id].expire = \
                time() + self._handlers[storage_id].cache.expiretime
            return self._handlers[storage_id]

        if storage is None or storage_id != storage.storage_id \
               or not storage.vcs_engine in self.vcs_classes:
            return

        self._handlers[storage_id] = Handler(self, storage)
        return self._handlers[storage_id]

    # -------------------------------------------------------------------------
    def progress(self, storage_ids, pending=False):
        """Return the progress of actions on storages.

        :param storage_ids: (list)
            Storage ID list.
        :param pending: (boolean, default=False)
            ``True`` if there is a pending work.
        :return: (tuple)
            Return a tuple such as ``(working, progress_list)``.

        ``working`` is a boolean indicating whether one of the storage is on
        progress. ``progress_list`` is a list of items like ``(status,
        message)``. See :class:`Handler` class.
        """
        self._cleanup()
        working = False
        prgrss = {}
        for storage_id in storage_ids:
            if storage_id in self._handlers:
                handler_prgrss = self._handlers[storage_id].progress()
                if handler_prgrss[0] != 'wait':
                    prgrss[storage_id] = handler_prgrss
                    working |= handler_prgrss[0] == 'run'
        return working | pending, prgrss

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete expired Handler."""
        now = time()
        for storage_id in self._handlers.keys():
            if self._handlers[storage_id].expire < now:
                if self._handlers[storage_id].progress()[0] != 'run':
                    del self._handlers[storage_id]


# =============================================================================
class Handler(object):
    """This class manages access to one storage.

    ``self.uid`` is the ID of the associated storage.

    ``self.expire`` is the deadline for this object.

    ``self.cache`` is a :class:`beaker.cache.Cache` instance.

    ``self.vcs`` is a :class:`~.lib.vcs.Vcs` instance.

    ``self._report`` is a tuple such as ``(status, message, expire, ttl)``
    where ``expire`` is the report validity date and ``status`` is one of the
    following:

    ``self._refresh`` is a tuple such as ``(time_to_refresh, refresh_period)``.

    * ``wait``: waiting
    * ``run``: in progress
    * ``error``: ended with error
    * ``end``: ended with success
    """

    # -------------------------------------------------------------------------
    def __init__(self, handler_manager, storage):
        """Constructor method.

        :param handler_manager: (:class:`HandlerManager` instance)
            Application :class:`HandlerManager` object.
        :param storage: (:class:`~.models.storages.Storage` instance).
        """
        self.uid = storage.storage_id
        self.cache = handler_manager.cache_manager.get_cache(
            'stg_%s' % self.uid,
            expire=int(handler_manager.settings.get('storage.cache', 3600)))
        self.expire = time() + self.cache.expiretime
        self.vcs = handler_manager.vcs_classes[storage.vcs_engine](
            join(handler_manager.settings['storage.root'], self.uid),
            storage.vcs_url, storage.vcs_user, decrypt(storage.vcs_password,
            handler_manager.settings['auth.key']))
        self._report = ('wait', None, 0,
            int(handler_manager.settings.get('storage.report_ttl', 12)))
        self._refresh = [0, int(storage.refresh)]
        self._thread = None

   # -------------------------------------------------------------------------
    def clone(self, request=None):
        """Launch an action to clone a storage.

        :param request: (:class:`pyramid.request.Request` instance, optional)
            Current request.
        """
        # Action directly...
        if request is None:
            return self.vcs.clone()

        # ...or in a thread
        if self.launch(request, self.vcs.clone):
            self._refresh[0] = time() + self._refresh[1]

    # -------------------------------------------------------------------------
    def synchronize(self, request, force=False):
        """Launch an action to synchronize storage with its source.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param force: (boolean, optional)
            Force synchronization even if period is not over.
        :return: (boolean)
            ``True`` if it really launch a synchronization.

        If ``force`` is ``False``, the synchronizaton is only done if the
        delay of ``synchro_period`` seconds has expired.
        """
        # Something to do?
        if not force and self._refresh[0] > time():
            self.expire = time() + self.cache.expiretime
            return False

        # Action directly...
        if request is None:
            self.report('run')
            if not self.vcs.pull_update(self):
                self._refresh[0] = time() + self._refresh[1]
                return True
            return False

        # ...or in a thread
        if self.launch(request, self.vcs.pull_update):
            self._refresh[0] = time() + self._refresh[1]
            return True
        return False

    # -------------------------------------------------------------------------
    def report(self, status, message=None):
        """Save a report.

        :param status: (string)
            Current status. See :class:`Handler` class.
        :param message: (string, optional)
            Message to write in report.
        :return: (string or ``None``)
            Message.
        """
        self._report = (
            status, message, time() + self._report[3], self._report[3])
        self.expire = time() + self.cache.expiretime
        return message

    # -------------------------------------------------------------------------
    def progress(self):
        """Return the progress of action on the storage.

        :return: (tuple)
            A tuple such as ``(status, message)``. See :class:`Handler` class.
        """
        if self._thread is not None and self._thread.is_alive():
            return ('run', None)
        if self._report[0] != 'wait' and self._report[2] < time():
            self.report('wait')
        return self._report[0:2]

    # -------------------------------------------------------------------------
    @cache_method()
    def dir_infos(self, path, sort):
        """List all files of a directory with VCS informations.

        :param path: (string)
            Relative path of the directory.
        :param sort: (string)
            A sort order among ``+name``, ``-name``, ``+size``, ``-size``,
            ``+date``, ``-date``.
        :return: (tuple)
            A tuple of list such as ``(dirs, files)``.

        See: :meth:`file_infos`.
        """
        dirs, files = walk(join(self.vcs.path, path)).next()[1:]
        dirs = self.file_infos(path, dirs)
        files = self.file_infos(path, files)

        # Sort
        key = {'size': lambda k: k[2], 'date': lambda k: k[3],
               }.get(sort[1:], lambda k: strxfrm(k[0].encode('utf8')))
        dirs = sorted(dirs, key=key, reverse=(sort[0] == '-'))
        files = sorted(files, key=key, reverse=(sort[0] == '-'))

        # Labels
        for item in dirs:
            item[2] = size_label(item[2], True)
            item[3] = age(item[3])
        for item in files:
            item[2] = size_label(item[2], False)
            item[3] = age(item[3])

        return dirs, files

    # -------------------------------------------------------------------------
    def file_infos(self, path, filenames):
        """Return a sorted list of informations such as
        ``(file_name, file_type, size, revision, user, date, message)`` on each
        file in ``filenames``.

        :param path: (string)
            Relative path to files.
        :param filenames: (list)
            List of files.
        :return: (list of tuples)
            A list of lists such as ``['README', 'plain', '45.7 Kio',
            '2 days', '16:0e0229a916f4', 'user1', 'Bug fixed']``
        """
        file_infos = []
        for filename in filenames:
            vcs_infos = self.vcs.file_infos(path, filename)
            if vcs_infos is None:
                continue
            fullname = join(self.vcs.path, path, filename)
            filetype = get_mime_type(fullname)[1]
            size = len(listdir(fullname)) if filetype == 'folder' \
                   else getsize(fullname)
            file_infos.append([filename, filetype, size,
                vcs_infos[0], vcs_infos[1], vcs_infos[2], vcs_infos[3]])

        return file_infos

    # -------------------------------------------------------------------------
    def upload(self, user, path, upload_file, filename, message):
        """Synchronize, remove files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param filename: (:class:`cgi.FieldStorage` instance)
            FieldStorage of the file to upload.
        :param filename: (string or `None``)
            Name of file to replace or ``None``.
        :param message: (string)
            Commit message.
        """
        # Check filename
        if filename is not None and filename != upload_file.filename:
            self.report('error', _('File names are different.'))
            return

        # Check repository
        if not self._check_repository(user, message):
            return

        # Upload files
        fullpath = join(self.vcs.path, path or '.')
        ext = splitext(upload_file.filename)[1]
        if ext != '.zip' or filename:
            filename = filename or upload_file.filename
            with open(join(fullpath, filename), 'w') as hdl:
                hdl.write(upload_file.file.read())
        else:
            unzip(upload_file.file, fullpath)

        # Add
        if self.vcs.add(path, self):
            return

        # Propagate
        if not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            self.report('end')

    # -------------------------------------------------------------------------
    def mkdir(self, path, name):
        """Make a directory.

        :param path: (string)
            Relative path to directory to create.
        :param name: (string)
            Name of directory to create.
        """
        if not self.synchronize(None, True):
            return
        if not self.vcs.mkdir(path, name, self):
            self.report('end')

    # -------------------------------------------------------------------------
    def add(self, user, path, message):
        """Synchronize, remove files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Add
        if self.vcs.add(path, self):
            return

        # Propagate
        if not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            self.report('end')

    # -------------------------------------------------------------------------
    def rename(self, user, path, filename, new_name, message):
        """Synchronize, rename a file and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param filename: (string)
            Name of file to move.
        :param new_name: (string)
            New name.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Move files
        if self.vcs.rename(path, filename, new_name, self):
            return

        # Propagate
        if not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            self.report('end')

    # -------------------------------------------------------------------------
    def remove(self, user, path, filenames, message):
        """Synchronize, remove files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param filenames: (list)
            Names of files to remove.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Remove files
        for filename in filenames:
            if self.vcs.remove(path, filename, self):
                return

        # Propagate
        if not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            self.report('end')

    # -------------------------------------------------------------------------
    def launch(self, request, action, args=(), kwargs=None):
        """Launch a new action in a thread.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param action: (function)
            Action to launch.
        :param args: (tuple, optional)
            Arguments for the action.
        :param kwargs: (dictionary, optional)
            Keyword arguments for the action.
        :return: (boolean)
            ``True`` if action has been launched.

        Only one action per storage at a time is possible.
        """
        # Is this storage undergoing an action?
        if self._thread is not None and self._thread.is_alive():
            request.session.flash(_('${i}: action already in progress.',
                {'i': self.uid}), 'alert')
            return False
        if self._thread is not None:
            del self._thread

        # Launch action
        kwargs = kwargs or {}
        if action.im_self is not self:
            kwargs['handler'] = self
        self._thread = Thread(
            target=action, name=self.uid, args=args, kwargs=kwargs)
        self._thread.start()
        self.expire = time() + self.cache.expiretime
        return True

    # -------------------------------------------------------------------------
    def _check_repository(self, user, message):
        """Wait for repository availability, synchronize and check push
        capacity.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param message: (string)
            Commit message.
        :return: (boolean)
        """
        k = 10
        while self._report[0] == 'run' and k:
            k -= 1
            sleep(1)
        if self._report[0] == 'run':
            self.report('error', _('storage is busy.'))
            return False

        work = self.synchronize(None, True) and \
            not self.vcs.commit_push(message, user[0], user[1], user[2], self)
        if work:
            return True

        self.vcs.revert_all(self)
        return False
