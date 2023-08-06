# $Id: publidoc2html_final.py 1292397d8520 2011/12/30 17:33:03 patrick $
"""LePrisme finalization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(engine, output):
    """Finalization.

    :param engine: (Engine object)
        Engine object on which it depends.
    :param output: (string)
        Full path to output directory.
    """
    engine.build.log(
        _('dummy finalization of "${f}"', {'f': basename(output)}))
