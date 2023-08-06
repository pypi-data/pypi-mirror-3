# $Id: publidoc2csv_post.py 1bf675707e75 2012/06/27 00:21:45 patrick $
"""LePrisme postprocess script."""

from publiforge.lib.utils import _


# =============================================================================
def main(engine, filename, fid, data):
    """Post process script.

    :param engine: (:class:`Engine` instance)
        Engine object on which it depends.
    :param filename: (string)
        Relative path to the original file to transform.
    :param fid: (string)
        File identifier.
    :param data: (string or `:class:lxml.etree.ElementTree` object)
        Data to transform in a string or in a tree.
    :return: (string, `:class:lxml.etree.ElementTree` object or ``None``)
        Modified data or ``None`` if fails.
    """
    # pylint: disable = I0011, W0613
    engine.build.log(_('${f}: dummy postprocess of "${f}"', {'f': fid}))
    return data
