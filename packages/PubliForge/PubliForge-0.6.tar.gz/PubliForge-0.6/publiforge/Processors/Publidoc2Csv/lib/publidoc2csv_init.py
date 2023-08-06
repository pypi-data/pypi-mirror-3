# $Id: publidoc2csv_init.py 4a9197d778b8 2012/05/15 07:47:16 patrick $
"""LePrisme initialization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(engine, output):
    """Initialization.

    :param engine: (Engine object)
        Engine object on which it depends.
    :param output: (string)
        Full path to output directory.
    """
    engine.build.log(
        _('dummy initialization of "${f}"', {'f': basename(output)}))
