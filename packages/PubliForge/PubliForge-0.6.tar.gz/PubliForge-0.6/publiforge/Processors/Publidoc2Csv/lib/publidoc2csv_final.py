# $Id: publidoc2csv_final.py 4a9197d778b8 2012/05/15 07:47:16 patrick $
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
