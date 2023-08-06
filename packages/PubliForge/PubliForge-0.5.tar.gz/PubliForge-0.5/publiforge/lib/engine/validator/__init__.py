# $Id: __init__.py b1ffa5a75b89 2012/02/19 23:23:01 patrick $
"""Validation engine."""

from ...utils import _


# =============================================================================
class Engine(object):
    """Main class for Validator engine."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build

    # -------------------------------------------------------------------------
    def start(self):
        """Start the engine."""
        self.build.stopped(_('Currently not implemented.'))
