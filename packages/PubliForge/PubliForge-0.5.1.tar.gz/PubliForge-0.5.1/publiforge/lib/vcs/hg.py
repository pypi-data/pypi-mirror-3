# $Id: hg.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
"""Storage with Mercurial Version Control management."""

import logging
from os import remove, renames, makedirs
from os.path import exists, join, isdir, getmtime
from shutil import rmtree
from datetime import datetime
from urllib2 import HTTPError
from mercurial import ui, hg, commands
from mercurial.error import Abort
from urllib2 import URLError
from tempfile import mkdtemp

from pyramid.i18n import TranslationString

from ...lib.utils import _
from ...lib.vcs import Vcs


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsMercurialUi(ui.ui):
    """Override Mercurial ui class for Pylons use."""
    # pylint: disable = I0011, R0904

    # -------------------------------------------------------------------------
    def __init__(self, src=None):
        """Contructor method."""
        super(VcsMercurialUi, self).__init__(src)
        self.handler = None

    # -------------------------------------------------------------------------
    def write(self, *args, **opts):
        """Write args in log as informations."""
        for arg in args:
            LOG.info(arg.strip())

    # -------------------------------------------------------------------------
    def write_err(self, *args, **opts):
        """Write args in log as errors."""
        for arg in args:
            LOG.error(arg.strip())
            if self.handler is not None:
                self.handler.report('error', arg.strip())


# =============================================================================
class VcsMercurial(Vcs):
    """Version control system with Mercurial."""

    engine = 'hg'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        super(VcsMercurial, self).__init__(path, url, user_id, password)
        self._ui = VcsMercurialUi()
        self._ui.setconfig('ui', 'interactive', 'no')
        self._ui.setconfig('ui', 'username', '-')
        self._ui.setconfig('web', 'cacerts', '')

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        self._ui.handler = handler
        try:
            commands.clone(self._ui, self._full_url(), self.path)
        except (Abort, HTTPError, URLError, OSError), error:
            if handler is not None:
                handler.report('error', error)
                if not exists(self.path):
                    makedirs(self.path)
            return error
        remove(join(self.path, '.hg', 'hgrc'))

    # -------------------------------------------------------------------------
    def pull_update(self, handler):
        """Pull changes and update.

        See abstract function :meth:`~.lib.vcs.Vcs.pull_update`.
        """
        if not exists(self.path):
            return
        try:
            if self.engine == 'local':
                commands.update(self._ui, self._repo(handler))
            else:
                commands.pull(self._ui, self._repo(handler),
                                     self._full_url(), update=True)
        except (Abort, HTTPError, URLError, OSError), error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes.

        See abstract function :meth:`~.lib.vcs.Vcs.commit_push`.
        """
        if not exists(self.path):
            return
        my_ui = VcsMercurialUi()
        my_ui.handler = handler
        my_ui.setconfig('ui', 'interactive', 'no')
        my_ui.setconfig('ui', 'username', name.encode('utf8') or user_id)
        my_ui.setconfig('web', 'cacerts', '')
        repo = hg.repository(my_ui, self.path)
        try:
            commands.commit(my_ui, repo, message=message.encode('utf8'))
            if self.engine != 'local':
                commands.push(my_ui, repo, self._full_url(user_id, password))
        except (Abort, HTTPError, URLError, OSError), error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def revert_all(self, handler):
        """Revert all files of the repository."""
        if not exists(self.path):
            return
        commands.revert(
            self._ui, self._repo(handler), all=True, no_backup=True)
        commands.update(self._ui, self._repo(handler), clean=True)

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        ctx = self._repo()['tip']
        if ctx.rev() == -1:
            return (datetime.fromtimestamp(getmtime(self.path)), -1, '-')
        return (datetime.fromtimestamp(ctx.date()[0]), ctx.rev(),
                ctx.user().partition('<')[0].decode('utf8'))

    # -------------------------------------------------------------------------
    def file_infos(self, path, filename):
        """Return information on a file.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        log = self.log(path, filename)
        if log is None:
            return
        return len(log) and log[0] \
            or (datetime.fromtimestamp(
                getmtime(self.full_path(path, filename))), '-', '-', '-')

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.lib.vcs.Vcs.log`.
        """
        filename = self._log_path(path, filename)
        if filename is None:
            return

        class Ui(VcsMercurialUi):
            """Ui class to retrieve file information."""
            # pylint: disable = I0011, R0904
            def __init__(self, src=None):
                super(Ui, self).__init__(src)
                self.log = []
                self._entry = None

            def write(self, *args, **opts):
                for arg in args:
                    if arg.startswith('changeset:'):
                        self._entry = [
                            '', int(arg[10:].partition(':')[0]), '', '']
                    elif arg.startswith('user:'):
                        self._entry[2] = arg[5:].strip()
                    elif arg.startswith('date:'):
                        self._entry[0] = arg[5:-6].strip()
                    elif arg.startswith('summary:'):
                        self._entry[3] = arg[8:].strip()
                        self.log.insert(0, self._entry)

        my_ui = Ui()
        my_ui.setconfig('ui', 'verbose', False)
        repo = hg.repository(my_ui, self.path)
        try:
            commands.log(my_ui, repo, filename, limit=str(limit),
                follow=limit > 1 and not isdir(filename),
                date=None, rev=None, user=None)
        except (Abort, HTTPError, URLError, OSError), error:
            return [(datetime.now(), '', '', error)]
        if not len(my_ui.log):
            return my_ui.log

        my_ui.log = sorted(my_ui.log, key=lambda k: k[1], reverse=True)[:limit]
        for k, entry in enumerate(my_ui.log):
            my_ui.log[k] = (
                datetime.strptime(entry[0], '%a %b %d %H:%M:%S %Y'),
                str(entry[1]), entry[2].partition('<')[0].decode('utf8'),
                entry[3].decode('utf8'))
        return my_ui.log

   # -------------------------------------------------------------------------
    def add(self, path, handler):
        """Add all new files in ``path``.

        See abstract function :meth:`~.lib.vcs.Vcs.add`.
        """
        path = self.full_path(path)
        if isinstance(path, TranslationString):
            return handler.report('error', path)
        if not exists(path):
            return
        warn = commands.add(self._ui, self._repo(handler), path)
        if warn:
            return handler.report('error', 'Rejected')

    # -------------------------------------------------------------------------
    def rename(self, path, filename, new_name, handler):
        """Rename a file."""
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        new_name = self.full_path(path, new_name)
        if isinstance(new_name, TranslationString):
            return handler.report('error', new_name)
        if exists(new_name):
            return handler.report('error', _('File already exists!'))
        try:
            commands.rename(self._ui, self._repo(handler), filename, new_name)
        except (HTTPError, URLError, OSError), error:
            return handler.report('error', error)
        except Abort, error:
            if exists(filename) and not exists(new_name):
                renames(filename, new_name)

    # -------------------------------------------------------------------------
    def remove(self, path, filename, handler):
        """Remove a file.

        See abstract function :meth:`~.lib.vcs.Vcs.remove`.
        """
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if not exists(filename):
            return
        try:
            commands.remove(
                self._ui, self._repo(handler), filename)
        except (Abort, HTTPError, URLError, OSError), error:
            return handler.report('error', error)
        if exists(filename):
            if isdir(filename):
                rmtree(filename)
            else:
                remove(filename)

    # -------------------------------------------------------------------------
    def revision(self, fullname, revision):
        """Retrieve a revision.

        See :meth:`~.lib.vcs.Vcs.revision`.
        """
        tmp_dir = mkdtemp(prefix='publiforge')
        tmp_fil = join(tmp_dir, 'output')
        err = commands.cat(
            self._ui, self._repo(), fullname, rev=revision, output=tmp_fil)
        if err:
            rmtree(tmp_dir)
            return
        with open(tmp_fil, 'rb') as hdl:
            content = hdl.read()
        rmtree(tmp_dir)
        return content

    # -------------------------------------------------------------------------
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision.

        See :meth:`~.lib.vcs.Vcs.diff`.
        """
        class Ui(VcsMercurialUi):
            """Ui class to retrieve file information."""
            # pylint: disable = I0011, R0904
            def __init__(self, src=None):
                super(Ui, self).__init__(src)
                self.diff = ''

            def write(self, *args, **opts):
                self.diff += ''.join(args)

        my_ui = Ui()
        repo = hg.repository(my_ui, self.path)
        try:
            commands.diff(my_ui, repo, fullname, rev=[revision])
        except RuntimeError, err:
            return err

        return my_ui.diff.decode('utf8')

    # -------------------------------------------------------------------------
    def _repo(self, handler=None):
        """Get a repository object.

        :param handler: (:class:`~.lib.handler.Handler` instance, optional)
            Owner of this action.
        :return: (:class:`mercurial.repo`)
        """
        if handler is not None:
            self._ui.handler = handler
        return hg.repository(self._ui, self.path)


# =============================================================================
class VcsLocal(VcsMercurial):
    """Version control system for local files."""

    engine = 'local'

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Initialize a Mercurial repository and copy source.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        self._ui.handler = handler
        commands.init(self._ui, self.path)
        repo = self._repo()
        commands.add(self._ui, repo)
        commands.commit(self._ui, repo, message='Initial commit')
