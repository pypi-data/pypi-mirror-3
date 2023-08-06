# $Id: publidoc2html_init.py 1292397d8520 2011/12/30 17:33:03 patrick $
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
