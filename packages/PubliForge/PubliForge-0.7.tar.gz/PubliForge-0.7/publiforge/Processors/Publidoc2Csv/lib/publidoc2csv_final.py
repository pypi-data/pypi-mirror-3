# $Id: publidoc2csv_final.py 1bf675707e75 2012/06/27 00:21:45 patrick $
"""LePrisme finalization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(engine):
    """Finalization.

    :param engine: (Engine object)
        Engine object on which it depends.
    """
    engine.build.log(
        _('dummy finalization of "${f}"', {'f': basename(engine.output)}))
