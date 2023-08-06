# $Id: hgsvn.py c0062fcc9f82 2012/07/22 19:34:51 patrick $
"""Storage with Subversion (via Mercurila) Version Control management."""

import logging
from urlparse import urlparse, urlunparse
from mercurial import extensions

from .hg import VcsMercurial


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsHgSubversion(VcsMercurial):
    """Version control system with Subversion via HgSubversion."""

    engine = 'hgsvn'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        scheme, netloc, urlpath, params, query, fragment = urlparse(str(url))
        url = urlunparse((
            'svn+%s' % scheme, netloc, urlpath, params, query, fragment))
        super(VcsHgSubversion, self).__init__(path, url, user_id, password)
        try:
            extensions.load(self._ui, 'hgsubversion', '')
        except ImportError, error:
            LOG.error(error)

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.hg.VcsMercurial.last_change`.
        """
        change = super(VcsHgSubversion, self).last_change()
        return change[0], change[1], change[2].partition('@')[0]

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.hg.VcsMercurial.log`.
        """
        my_log = super(VcsHgSubversion, self).log(path, filename, limit)
        return my_log and \
            [(k[0], k[1], k[2].partition('@')[0], k[3]) for k in my_log]
