# $Id: svn.py a3fdbdf20e7f 2012/04/12 08:13:52 patrick $
"""Storage with Subversion Version Control management."""

import logging
from urlparse import urlparse, urlunparse
from mercurial import extensions

from .hg import VcsMercurial


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsSubversion(VcsMercurial):
    """Version control system with Subversion."""

    engine = 'svn'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        scheme, netloc, urlpath, params, query, fragment = urlparse(str(url))
        url = urlunparse((
            'svn+%s' % scheme, netloc, urlpath, params, query, fragment))
        super(VcsSubversion, self).__init__(path, url, user_id, password)
        try:
            extensions.load(self._ui, 'hgsubversion', '')
        except ImportError, error:
            LOG.error(error)

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes.

        See method :meth:`~.hg.VcsMercurial.commit_push`.
        """
        super(VcsSubversion, self).commit_push(
            message, user_id, password, name, handler)

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.hg.VcsMercurial.last_change`.
        """
        change = super(VcsSubversion, self).last_change()
        return change[0], change[1], change[2].partition('@')[0]

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.hg.VcsMercurial.log`.
        """
        my_log = super(VcsSubversion, self).log(path, filename, limit)
        return my_log and \
               [(k[0], k[1], k[2].partition('@')[0], k[3]) for k in my_log]
