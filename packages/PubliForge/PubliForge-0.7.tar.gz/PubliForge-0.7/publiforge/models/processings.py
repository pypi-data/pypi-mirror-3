# $Id: processings.py c0062fcc9f82 2012/07/22 19:34:51 patrick $
"""SQLAlchemy-powered model definition for project processings."""

from lxml import etree
from textwrap import fill
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_spaces, export_file_set
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, VALUE_LEN
from . import Base, DBSession
from .users import User


ADD2PACK_TARGETS = {
    'result2files': _('result in files'),
    'result2resources': _('result in resources'),
    'result2templates': _('result in templates'),
    'output2files': _('full output in files'),
    'output2resources': _('full output in resources'),
    'output2templates': _('full output in templates')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Processing(Base):
    """SQLAlchemy-powered project processing model."""
    # pylint: disable = I0011, W0142

    __tablename__ = 'processings'
    __table_args__ = (
        UniqueConstraint('project_id', 'label'), {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer,
        ForeignKey('projects.project_id', ondelete='CASCADE'),
        primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    processor = Column(types.String(ID_LEN), nullable=False)
    output = Column(types.String(PATH_LEN))
    add2pack = Column(
        types.Enum(*ADD2PACK_TARGETS.keys(), name='add2pack_type_enum'))
    variables = relationship('ProcessingVariable')
    user_variables = relationship('ProcessingUserVariable')
    files = relationship('ProcessingFile')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description, processor, output=None,
                 add2pack=None):
        """Constructor method."""
        # pylint: disable = I0011, R0913
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.processor = processor.strip()[0:ID_LEN]
        self.output = output and output.strip()[0:PATH_LEN]
        self.add2pack = add2pack

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, processing_elt, check_if_exists=True):
        """Load a processing from a XML file.

        :param processing_elt: (:class:`lxml.etree.Element` instance)
            Processing XML element.
        :param check_if_exists: (boolean, default=True)
            Check if processing already exists before inserting.
        :return: (:class:`pyramid.i18n.TranslationString` or integer)
            Error message or integer.
        """
        if processing_elt is None:
            return _('nothing to do!')

        label = normalize_spaces(processing_elt.findtext('label'), LABEL_LEN)
        if check_if_exists:
            processing = DBSession.query(cls).filter_by(
                project_id=project_id, label=label).first()
            if processing is not None:
                return _('Processing "${l}" already exists.', {'l': label})

        output = processing_elt.find('output')
        processing = cls(
            project_id, label,
            processing_elt.findtext('description'),
            processing_elt.findtext('processor').strip(),
            output is not None and output.text or None,
            output is not None and output.get('add2pack') or None)

        # Load variables
        cls._load_variables(processing_elt, processing)

        # Load resources and templates
        for child in processing_elt.iterdescendants(tag=etree.Element):
            if child.tag in ('resource', 'template'):
                processing.files.append(ProcessingFile(
                    child.tag, child.text.strip(), child.get('to'),
                    child.get('visible')))

        DBSession.add(processing)
        DBSession.commit()
        return processing.processing_id

    # -------------------------------------------------------------------------
    @classmethod
    def correct_processing_variables(cls, project_id, processings):
        """Correct values of processing type variables according to
        ``processings`` dictionary.

        :param project_id: (integer)
            Project ID.
        :param processings: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        """
        # Correct default values
        for var in DBSession.query(ProcessingVariable)\
                .filter_by(project_id=project_id):
            if var.name.startswith('processing') \
                    and var.default in processings:
                var.default = 'prc%d.%d' % (
                    project_id, processings[var.default])

        # Correct user values
        for var in DBSession.query(ProcessingUserVariable)\
                .filter_by(project_id=project_id):
            if var.name.startswith('processing') and var.value in processings:
                var.value = 'prc%d.%d' % (project_id, processings[var.value])

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, processor):
        """Serialize a processing to a XML representation.

        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (:class:`lxml.etree.Element`)
        """
        proc_elt = etree.Element('processing')
        proc_elt.set('%sid' % XML_NS,
                     'prc%d.%d' % (self.project_id, self.processing_id))
        etree.SubElement(proc_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(proc_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        etree.SubElement(proc_elt, 'processor').text = self.processor
        if processor is not None:
            self.export_variables(proc_elt, processor)
        export_file_set(proc_elt, self, 'resource')
        export_file_set(proc_elt, self, 'template')
        if self.output:
            elt = etree.SubElement(proc_elt, 'output')
            elt.text = self.output
            if self.add2pack:
                elt.set('add2pack', self.add2pack)

        return proc_elt

    # -------------------------------------------------------------------------
    def export_variables(self, proc_elt, processor):
        """Read variable definitions in processor tree and fill ``variables``
        XML structure.

        :param proc_elt: (:class:`lxml.etree.Element` instance)
            Processing element that binds the result.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        """
        # Read default values
        defaults = dict([
            (k.name, (k.default, k.visible)) for k in self.variables])

        # Read user values
        values = {}
        for var in self.user_variables:
            values[var.name] = var.name in values \
                and values[var.name] + [(var.value, var.user_id)] \
                or [(var.value, var.user_id)]
        if len(defaults) == 0 and len(values) == 0:
            return

        # Browse processor variables
        users = None
        vars_elt = etree.Element('variables')
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            default = defaults[name][0] if name in defaults \
                and defaults[name][0] is not None else var.findtext('default')
            elt = etree.Element('var', name=name)
            if name in values:
                for value in values[name]:
                    if users is None:
                        users = dict(DBSession.query(User.user_id, User.login))
                    if value[0] != default and value[1] in users:
                        etree.SubElement(elt, 'value', user=users[value[1]])\
                            .text = value[0]
            if name in defaults:
                if default is not None and default != var.findtext('default'):
                    etree.SubElement(elt, 'default').text = default
                if defaults[name][1] is not None and \
                        bool(defaults[name][1]) != bool(var.get('visible')):
                    elt.set('visible', str(defaults[name][1]).lower())
            if len(elt) or elt.get('visible') is not None:
                vars_elt.append(elt)

        if len(vars_elt):
            proc_elt.append(vars_elt)

    # -------------------------------------------------------------------------
    def export_user_variables(self, proc_elt, processor, values):
        """Read variable definitions in processor tree and fill ``variables``
        XML structure for a build.

        :param proc_elt: (:class:`lxml.etree.Element` instance)
            Processing element that binds the result.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param values: (dictionary)
            Variables values.
        """
        # Read default values
        defaults = dict([(k.name, k.default) for k in self.variables])

        vars_elt = etree.Element('variables')
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            value = values[name] if name in values \
                else (defaults[name] if name in defaults
                      and defaults[name] is not None else None)
            if value is not None and var.get('type') == 'boolean':
                value = value and 'true' or 'false'
            if value is not None and value != var.findtext('default'):
                etree.SubElement(vars_elt, 'var', name=name).text = value

        if len(vars_elt):
            proc_elt.append(vars_elt)

    # -------------------------------------------------------------------------
    @classmethod
    def _load_variables(cls, root_elt, processing):
        """Import variables from XML.

        :param root_elt: (:class:`lxml.etree.Element` instance)
            Element to browse.
        :param processing: (:class:`Processing`)
            Model to complete.
        """
        users = None
        for child in root_elt.iterdescendants(tag=etree.Element):
            if child.tag != 'var':
                continue

            if child.get('visible') is not None \
                    or child.find('default') is not None:
                processing.variables.append(ProcessingVariable(
                    child.get('name'), child.findtext('default'),
                    child.get('visible')))

            for value in child.findall('value'):
                if users is None:
                    users = dict(DBSession.query(User.login, User.user_id))
                if value.get('user') in users:
                    processing.user_variables.append(ProcessingUserVariable(
                        users[value.get('user')], child.get('name'),
                        value.text))


# =============================================================================
class ProcessingVariable(Base):
    """SQLAlchemy-powered project processing variable model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'processings_variables'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processings.project_id', 'processings.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    name = Column(types.String(ID_LEN), primary_key=True)
    default = Column(types.String(VALUE_LEN))
    visible = Column(types.Boolean)

    # -------------------------------------------------------------------------
    def __init__(self, name, default, visible=None):
        """Constructor method."""
        self.name = name.strip()[0:ID_LEN]
        self.default = \
            isinstance(default, basestring) and default[0:VALUE_LEN] or default
        if visible is not None:
            self.visible = \
                visible if isinstance(visible, bool) else (visible == 'true')


# =============================================================================
class ProcessingUserVariable(Base):
    """SQLAlchemy-powered project processing variable model for each user."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'processings_users_variables'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processings.project_id', 'processings.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    user_id = Column(
        types.Integer, ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True)
    name = Column(types.String(ID_LEN), primary_key=True)
    value = Column(types.String(VALUE_LEN))

    # -------------------------------------------------------------------------
    def __init__(self, user_id, name, value):
        """Constructor method."""
        self.user_id = user_id
        self.name = name.strip()[0:ID_LEN]
        self.value = \
            isinstance(value, basestring) and value[0:VALUE_LEN] or value


# =============================================================================
class ProcessingFile(Base):
    """SQLAlchemy-powered project processing file model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'processings_files'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processings.project_id', 'processings.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    file_type = Column(
        types.Enum('resource', 'template', name='prcfil_type_enum'),
        primary_key=True)
    path = Column(types.String(PATH_LEN), primary_key=True)
    target = Column(types.String(PATH_LEN))

    # -------------------------------------------------------------------------
    def __init__(self, file_type, path, target=None, visible=None):
        """Constructor method."""
        # pylint: disable = I0011, W0613
        self.file_type = file_type
        self.path = path.strip()[0:PATH_LEN]
        self.target = (target and target.strip()[0:PATH_LEN]) \
            or (file_type == 'template' and
                self.path.partition('/')[2][0:PATH_LEN]) or None
