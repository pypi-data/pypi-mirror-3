# $Id: publidoc2csv_pre.py 4a9197d778b8 2012/05/15 07:47:16 patrick $
"""LePrisme preprocess script."""

from publiforge.lib.utils import _


# =============================================================================
def main(engine, filename, fid, data, output):
    """Preprocess script.

    :param engine: (:class:`Engine` instance)
        Engine object on which it depends.
    :param filename: (string)
        Relative path to the original file to transform.
    :param fid: (string)
        File identifier.
    :param data: (string or `:class:lxml.etree.ElementTree` object)
        Data to transform in a string or in a tree.
    :param output: (string)
        Full path to output directory.
    :return: (string, `:class:lxml.etree.ElementTree` object or ``None``)
        Modified data or ``None`` if fails.
    """
    # pylint: disable = I0011, W0613
    engine.build.log(_('${f}: dummy preprocess of "${f}"', {'f': fid}))
    return data
