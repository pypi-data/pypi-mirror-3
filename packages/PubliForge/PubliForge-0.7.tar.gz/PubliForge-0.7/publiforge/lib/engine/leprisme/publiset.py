# $Id: publiset.py a1a9a52da6b1 2012/08/09 12:57:40 patrick $
"""Publiset management."""

from os.path import join, basename, splitext, normpath
from lxml import etree
from copy import deepcopy

from ...utils import _
from ...xml import XML_NS, load

PUBLIDOC_VERSION = '1.0'
PUBLISET_VERSION = '1.0'


# =============================================================================
class Publiset(object):
    """Class for Publiset management."""

    # -------------------------------------------------------------------------
    def __init__(self, engine, base_path):
        """Constructor method.

        :param engine: (:class:`~.lib.engine.leprisme.Engine` instance)
            Engine object on which it depends.
        :param base_path: (string)
            Base path for files in publiset.
        """
        self._engine = engine
        self._base_path = base_path

    # -------------------------------------------------------------------------
    def fullname(self, file_elt):
        """Find the full path of a file from a file tag.

        :pgaram file_elt: (etree.Element object)
             File element.
        :return: (string)
             Full path name.
        """
        elt = file_elt.getparent()
        while elt is not None and elt.get('path') is None:
            elt = elt.getparent()

        if elt is None:
            return join(self._base_path, file_elt.get('name'))
        return normpath(join(
            self._base_path, elt.get('path'), file_elt.get('name')))

    # -------------------------------------------------------------------------
    def compose(self, filename, set_root):
        """Compose an XML document from a publiset XML composition.

        :param filename: (string)
            Name of the composition file.
        :param set_root: (:class:`lxml.etree.Element` instance)
            ``composition`` element.
        :return: (etree.ElementTree object)
            Document tree or ``None``.
        """
        # Document root element
        doc_root = self._doc_element(
            set_root, 'publidoc', {'version': PUBLIDOC_VERSION})

        # Browse structure
        for elt in set_root.iterchildren(tag=etree.Element):
            if not self._append(elt, doc_root):
                return
        doc_root = etree.ElementTree(doc_root)

        # Validate
        if self._engine.config('Input', 'validate') == 'true':
            error = load(filename, self._engine.relaxngs, doc_root)
            if isinstance(error, basestring):
                self._engine.build.stopped(error, 'a_error')
                return

        return doc_root

    # -------------------------------------------------------------------------
    @classmethod
    def create(cls, element):
        """Create an empty ``publiset`` document and fill it with ``element``.

        :param element: (:class:`lxml.etree.Element` instance)
            Main element.
        :return: (etree.ElementTree)
        """
        root = etree.Element('publiset', version=PUBLISET_VERSION)
        root.append(element)
        return etree.ElementTree(root)

    # -------------------------------------------------------------------------
    def _append(self, set_current, doc_current):
        """Append ``set_current`` to ``doc_current`` element, converting tag
        and attribute names.

        :param set_current: (:class:`lxml.etree.Element` instance)
            Publiset element.
        :param doc_current: (:class:`lxml.etree.Element` instance)
            Target document element.
        :return: (boolean)
        """
        if set_current.tag == 'file':
            return self._append_file(set_current, doc_current)

        # Browse
        doc_elt = self._doc_element(set_current)
        for set_elt in set_current.iterchildren(tag=etree.Element):
            if not self._append(set_elt, doc_elt):
                return False
        if set_current.get('transform') is None:
            doc_current.append(doc_elt)
            return True

        # Transform
        xslfile = join(self._engine.build.path, 'Processor', 'Xsl',
                       set_current.get('transform'))
        try:
            transform = etree.XSLT(etree.parse(xslfile))
        except (IOError, etree.XSLTParseError, etree.XMLSyntaxError), err:
            self._engine.build.stopped(
                str(err).replace(self._engine.build.path, '..'))
            return False
        try:
            for doc_elt in transform(doc_elt).xpath('/*'):
                doc_current.append(doc_elt)
        except (etree.XSLTApplyError, AssertionError), err:
            self._engine.build.stopped(err, 'a_error')
            return False
        return True

    # -------------------------------------------------------------------------
    def _append_file(self, file_elt, doc_current):
        """Append file content as child of ``doc_current``.

        :param file_elt: (:class:`lxml.etree.Element` instance)
             File element.
        :param doc_current: (:class:`lxml.etree.Element` instance)
            Target document element.
        :return: (boolean)
        """
        # Load file
        # pylint: disable = I0011, E1103, R0911
        relaxngs = self._engine.relaxngs \
            if self._engine.config('Input', 'validate') == 'true' else None
        filename = self.fullname(file_elt)
        if not filename.startswith(self._engine.build.data_path):
            self._engine.build.stopped(_(
                '${f}: file outside storage area', {'f': basename(filename)}))
            return False
        tree = load(filename, relaxngs)
        if isinstance(tree, basestring):
            self._engine.build.stopped(tree, 'a_error')
            return False

        # XSL transformation...
        set_elt = file_elt
        while set_elt is not None and set_elt.get('xslt') is None:
            set_elt = set_elt.getparent()
        if set_elt is not None:
            fid = '"%s"' % splitext(basename(filename))[0]
            filename = join(self._engine.build.path, 'Processor', 'Xsl',
                            set_elt.get('xslt'))
            try:
                xslt = etree.XSLT(etree.parse(filename))
            except (IOError, etree.XSLTParseError, etree.XMLSyntaxError), err:
                self._engine.build.stopped(
                    str(err).replace(self._engine.build.path, '..'))
                return False
            try:
                for child in xslt(tree, fid=fid)\
                        .xpath('/*|/processing-instruction()'):
                    doc_current.append(child)
            except (etree.XSLTApplyError, AssertionError), err:
                self._engine.build.stopped(err, 'a_error')
                return False
            return True

        # ...or XPath
        set_elt = file_elt
        while set_elt is not None and set_elt.get('xpath') is None:
            set_elt = set_elt.getparent()
        if set_elt is not None:
            try:
                for child in tree.xpath(set_elt.get('xpath')):
                    doc_current.append(child)
            except etree.XPathEvalError, err:
                self._engine.build.stopped('XPath: %s' % err, 'a_error')
                return False
        else:
            doc_current.append(deepcopy(tree.getroot()))

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _doc_element(cls, set_elt, default_tag=None, default_atts=None):
        """Create a document element from a set element according to its ``as``
        and ``attributes`` attributes.

        :param set_elt: (:class:`lxml.etree.Element` instance)
            Source element
        :param default_tag: (string)
            If ``default_tag`` is None and ``as`` attribute doesn't exist, the
            ``set_elt`` name is used as tag name.
        :param default_atts: (dictionary)
            If ``default_atts`` is None and ``attributes`` attribute doesn't
            exist, ``set_elt`` attributes are copied.
        :return: (ElementTree)
        """
        # Tag
        if default_tag is None:
            default_tag = set_elt.tag
        doc_elt = etree.Element(set_elt.get('as', default_tag))

        # Attributes
        atts = set_elt.get('attributes', '').split()
        if atts:
            atts = dict([(i.split('=')[0], i.split('=')[1]) for i in atts])
        else:
            atts = default_atts or set_elt.attrib
        for att, value in atts.items():
            if att not in \
                    ('as', 'attributes', 'transform', 'path', 'xslt', 'xpath'):
                doc_elt.set(att.replace('xml:', XML_NS), value)

        # Text
        doc_elt.text = set_elt.text
        doc_elt.tail = set_elt.tail

        return doc_elt
