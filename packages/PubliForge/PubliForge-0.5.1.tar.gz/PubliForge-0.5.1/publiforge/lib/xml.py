# $Id: xml.py 4526d61fab90 2012/03/11 17:47:45 patrick $
"""XML manipulation."""

from os.path import join, dirname,  basename
from lxml import etree
from cStringIO import StringIO

from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response

from .utils import _, has_permission, normalize_name
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.projects import Project


XML_NS = '{http://www.w3.org/XML/1998/namespace}'
PUBLIFORGE_RNG_VERSION = '1.0'


# =============================================================================
def load(filename, relaxngs=None, data=None):
    """Load an XML document and validate it against a Relax NG file.

    :param filename: (string)
        Name of XML file.
    :param relaxngs: (dictionary, optional)
        Relax NG dictionary such as ``{<pattern>: <relax_ng_file>,...}``. If it
        is ``None``, no validation is performed.
    :param data: (string or :class:`ElementTree`, optional)
        Content of the XML document. If it is not ``None``, it is used in place
        of the content of the file ``filename``.
    :return: (string, :class:`TranslationString` or :class:`ElementTree`)
        An error message or an instance of :class:`lxml.etree.ElementTree`
        class.
    """
    # pylint: disable = I0011, R0911
    # Read file
    if data is None or isinstance(data, basestring):
        try:
            tree = etree.parse(filename if data is None else StringIO(data))
        except IOError, err:
            return str(err).replace('%s/' % dirname(filename), '')
        except etree.XMLSyntaxError, err:
            return _('${name} not well-formed: ${err}',
                     {'name': basename(filename), 'err': str(err)})
    else:
        tree = data

    # Find RelaxNG
    if relaxngs is None:
        return tree
    if tree.getroot().tag not in relaxngs:
        return _('${tag}: Relax NG not found', {'tag': tree.getroot().tag})
    relaxng = relaxngs[tree.getroot().tag]

    # Load RelaxNG
    if isinstance(relaxng, basestring):
        try:
            relaxng = etree.RelaxNG(etree.parse(relaxng))
        except IOError, err:
            return str(err).replace('%s/' % dirname(filename), '')
        except (etree.XMLSyntaxError, etree.RelaxNGParseError), err:
            return '"%s": %s' % (relaxng, err)

    # Validate
    if not relaxng.validate(tree):
        return str(relaxng.error_log.last_error)\
               .replace('%s/' % dirname(filename), '')\
               .replace(':ERROR:RELAXNGV', '')

    return tree


# =============================================================================
def local_text(root_elt, xpath, request=None, lang=None, default=''):
    """Return the text in local language of the ``root_elt`` element child
    selected by ``xpath``.

    :param root_elt: (:class:`lxml.etree.Element` instance)
        Root element.
    :param xpath: (string)
        XPath expression.
    :param request: (:class:`pyramid.request.Request` instance, optional)
        Current request.
    :param lang: (string, optional)
        Preferred language.
    :param default: (string, optional)
        Default label.
    :return: (string)

    If label does not exist in the asked language, this method returns the
    label in default language or in english or the first label or ''.
    """
    if lang is None and request is None:
        return default

    lang = lang or request.session['lang']
    lang_xpath = xpath + '[@xml:lang="%s"]'
    text = root_elt.xpath(lang_xpath % lang) \
           or root_elt.xpath(lang_xpath % lang.split('_')[0])
    if not len(text) and request is not None:
        lang = request.registry.settings['pyramid.default_locale_name']
        text = root_elt.xpath(lang_xpath % lang) \
               or root_elt.xpath(lang_xpath % lang.split('_')[0])
    if not len(text):
        text = root_elt.xpath(lang_xpath % 'en')

    text = (len(text) == 1 and text[0].text) or \
           (root_elt.find(xpath) and root_elt.find(xpath).text) or default

    return ' '.join(text.split()).strip()


# =============================================================================
def import_configuration(settings, filename, only=None, error_if_exists=True,
                         xml=None, request=None):
    """Import a XML configuration file.

    :param settings: (dictionary)
        Application settings
    :param filename: (string)
        Full path to file to import.
    :param only: (string, optional)
        ``user``, ``group``, ``storage`` or ``project``.
    :param error_if_exists: (boolean, default=True)
        It returns an error if an item already exists.
    :param xml: (string, optional)
        Content of the XML document.
    :param request: (:class:`pyramid.request.Request` instance, optional)
        Current request.
    :return: (list)
        A list of error messages.
    """
    # Load XML
    tree = load(filename, {'publiforge':
        join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}, xml)
    if isinstance(tree, basestring):
        return (tree,)

    # Load users
    # pylint: disable = I0011, E1103
    errors = []
    if only is None or only == 'user':
        for elt in tree.xpath('user|users/user'):
            errors.append(User.load(settings, elt, error_if_exists))

    # Load groups
    if only is None or only == 'group':
        for elt in tree.xpath('group|groups/group'):
            errors.append(Group.load(elt, error_if_exists))

    # Load storages
    if only is None or only == 'storage':
        for elt in tree.xpath('storage|storages/storage'):
            storage = Storage.load(settings, elt, error_if_exists)
            if isinstance(storage, basestring):
                errors.append(storage)
            elif storage is not None and request is not None:
                handler = request.registry['handler']\
                      .get_handler(storage.storage_id, storage)
                handler.clone(request)

    # Load projects
    if only is None or only == 'project':
        for elt in tree.xpath('project|projects/project'):
            errors.append(Project.load(elt, error_if_exists))

    return [k for k in errors if k is not None]


# =============================================================================
def upload_configuration(request, perm, only=None):
    """Upload a XML configuration file.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param perm: (string)
        Level of permission needed.
    :param only: (string, optional)
        ``user``, ``group``, ``storage`` or ``project``.
    """
    if not has_permission(request, perm):
        raise HTTPForbidden()

    xml_file = request.params.get('xml_file')
    if isinstance(xml_file, basestring):
        return

    errors = import_configuration(
        request.registry.settings, xml_file.filename, only=only,
        xml=xml_file.file.read(), request=request)
    for error in errors:
        request.session.flash(error, 'alert')


# =============================================================================
def export_configuration(elements, filename=None, command=False):
    """Export an XML configuration and return it as a
    :class:`pyramid.response.Response` object.

    :param elements: (list)
        List of :class:`lxml.etree.Element` objects.
    :param filename: (string, optional)
        Name of file to export. Default to ``'publiforge'``.
    :param command: (boolean, default=False)
        ``True`` if called by command line.
    :return: (:class:`pyramid.response.Response` instance)
    """
    def _label(elt):
        """Get label or name of ``elt``."""
        label = elt.get('%sid' % XML_NS) or elt.get('login') \
            or (elt.findtext('label') is not None and elt.findtext('label'))
        return u' '.join(label.strip().split())

    # Nothing to do
    if len(elements) == 0:
        raise HTTPForbidden()

    # Create XML document
    root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)

    # Single export
    if len(elements) == 1:
        label = _label(elements[0])
        root.append(etree.Comment('=' * 70))
        root.append(etree.Comment(u'{0:^70}'.format(label)))
        root.append(etree.Comment('=' * 70))
        root.append(elements[0])
        filename = '%s.pf%s' % (label, elements[0].tag[0])
    # Multiple export
    else:
        for name in ('user', 'group', 'storage', 'project', 'processing'):
            elts = [k for k in elements if k is not None and k.tag == name]
            if not len(elts):
                continue
            root.append(etree.Comment('=' * 70))
            root.append(etree.Comment(u'{0:^70}'.format(
                '%ss' % name.capitalize())))
            root.append(etree.Comment('=' * 70))
            grouper = etree.SubElement(root, '%ss' % name)
            for elt in elts:
                grouper.append(etree.Comment(' ' * 68))
                grouper.append(etree.Comment(
                    u'{0:=^68}'.format(' %s ' % _label(elt))))
                grouper.append(etree.Comment(' ' * 68))
                grouper.append(elt)
        filename = filename or 'publiforge'

    # Command line
    if command:
        root = etree.ElementTree(root)
        root.write(filename, pretty_print=True, encoding='utf-8',
                    xml_declaration=True)
        return

    # Response
    response = Response(body=etree.tostring(
        root, pretty_print=True, encoding='utf-8', xml_declaration=True),
        content_type='application/xml')
    response.headerlist.append(('Content-Disposition',
        'attachment; filename="%s.xml"' % normalize_name(filename)))
    return response
