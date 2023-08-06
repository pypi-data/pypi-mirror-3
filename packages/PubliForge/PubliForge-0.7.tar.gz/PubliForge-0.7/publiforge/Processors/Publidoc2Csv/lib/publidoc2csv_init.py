# $Id: publidoc2csv_init.py 1bf675707e75 2012/06/27 00:21:45 patrick $
"""LePrisme initialization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(engine):
    """Initialization.

    :param engine: (Engine object)
        Engine object on which it depends.
    """
    engine.build.log(
        _('dummy initialization of "${f}"', {'f': basename(engine.output)}))
