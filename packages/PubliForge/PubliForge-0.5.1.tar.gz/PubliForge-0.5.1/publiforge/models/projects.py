# $Id: projects.py 86b088d85a5a 2012/03/21 22:20:47 patrick $
"""SQLAlchemy-powered model definition for projects."""

from lxml import etree
from textwrap import fill
from datetime import datetime
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_name
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, VALUE_LEN
from . import Base, DBSession
from .users import User
from .groups import Group


PROJECT_STATUS = {'draft': _('Draft'), 'active': _('Active'),
                  'archived': _('Archived')}
PROJECT_PERMS = {'editor': _('Leader'), 'user': _('User')}


# =============================================================================
class Project(Base):
    """SQLAlchemy-powered project model."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'projects'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    status = Column(types.Enum(*PROJECT_STATUS.keys(), name='prj_status_enum'),
                    nullable=False, default='active')
    deadline = Column(types.Date)
    users = relationship('ProjectUser', backref='project')
    groups = relationship('ProjectGroup')
    processings = relationship('ProjectProcessing')
    packs = relationship('ProjectPack')

    # -------------------------------------------------------------------------
    def __init__(self, label, description=None, status=None, deadline=None):
        """Constructor method."""
        self.label = u' '.join(label.strip().split())[0:LABEL_LEN]
        if description:
            self.description = \
                u' '.join(description.strip().split())[0:DESCRIPTION_LEN]
        self.status = status
        if deadline is not None:
            self.deadline = (isinstance(deadline, basestring)
                and datetime.strptime(deadline, '%Y-%m-%d')) or deadline

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return u"<Project({project_id}, '{label}', '{status}')>".format(
            project_id=self.project_id or -1, label=self.label,
            status=self.status).encode('utf8')

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_elt, error_if_exists=True):
        """Load a project from a XML file.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if project already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        label = u' '.join(
            project_elt.findtext('label').strip().split())[0:LABEL_LEN]
        project = DBSession.query(cls).filter_by(label=label).first()
        if project is not None:
            if error_if_exists:
                return _('Project "${l}" already exists.', {'l': label})
            return

        # Create project
        project = cls(project_elt.findtext('label'),
                      project_elt.findtext('description'),
                      project_elt.get('status', 'active'),
                      project_elt.findtext('deadline'))
        DBSession.add(project)
        DBSession.commit()

        # Append processings
        elt = project_elt.find('processings')
        if elt is not None:
            for child in elt.iterchildren(tag=etree.Element):
                ProjectProcessing.load(project.project_id, child, False)

        # Append packs
        elt = project_elt.find('packs')
        if elt is not None:
            for child in elt.iterchildren(tag=etree.Element):
                ProjectPack.load(project.project_id, child)

        # Add users
        done = []
        for item in project_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if not login in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    project.users.append(ProjectUser(
                        project.project_id, user.user_id, item.get('in-menu'),
                        item.get('permission', 'user')))
                done.append(login)

        # Add groups
        done = []
        for item in project_elt.findall('members/member-group'):
            group_id = normalize_name(item.text)[0:ID_LEN]
            if group_id not in done:
                done.append(group_id)
                group = DBSession.query(Group).filter_by(
                    group_id=group_id).first()
                if group is not None:
                    project.groups.append(ProjectGroup(project.project_id,
                        group.group_id, item.get('permission', 'user')))

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, request):
        """Serialize a project to a XML representation.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (:class:`lxml.etree.Element`)
        """
        # Header
        project_elt = etree.Element('project')
        project_elt.set('status', self.status)
        etree.SubElement(project_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(project_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 8,
                subsequent_indent=' ' * 8)
        if self.deadline:
            etree.SubElement(project_elt, 'deadline')\
                .text = self.deadline.isoformat()

        # Processings
        if self.processings:
            group_elt = etree.SubElement(project_elt, 'processings')
            for processing in self.processings:
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Processing: %s ' % processing.label)))
                processor = request.registry['fbuild'].processor(
                    request, processing.processor)
                group_elt.append(processing.xml(processor))

        # Packs
        if self.packs:
            group_elt = etree.SubElement(project_elt, 'packs')
            for pack in self.packs:
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Pack: %s ' % pack.label)))
                group_elt.append(pack.xml())

        # Team
        if self.users or self.groups:
            project_elt.append(etree.Comment(u'{0:~^66}'.format(' Team ')))
            group_elt = etree.SubElement(project_elt, 'members')
            for user in self.users:
                elt = etree.SubElement(group_elt, 'member')
                elt.text = user.user.login
                if user.perm != 'user':
                    elt.set('permission', user.perm or 'none')
                if user.in_menu:
                    elt.set('in-menu', 'true')
            for group in self.groups:
                elt = etree.SubElement(group_elt, 'member-group')
                elt.text = group.group_id
                if group.perm != 'user':
                    elt.set('permission', group.perm)

        return project_elt

    # -------------------------------------------------------------------------
    @classmethod
    def load_set(cls, root_elt, record, file_class):
        """Load set of files or variables.

        :param root_elt: (:class:`lxml.etree.Element` instance)
            Element to browse
        :param record: (:class:`~.models.projects.ProjectProcessing`
            or :class:`~.models.projects.ProjectPack` instance).
        :param file_class:
            (:class:`~.models.projects.ProjectProcessingFile`
            or :class:`~.models.projects.ProjectPackFile)`
            File class.
         """
        for child in root_elt.iterdescendants(tag=etree.Element):
            if child.tag == 'var':
                value = child.findtext('value') is not None \
                        and child.findtext('value').strip() or ''
                record.variables.append(ProjectProcessingVariable(
                    child.get('name'), value,
                    child.findtext('default') is not None
                    and child.findtext('default').strip() or value,
                    child.get('visible')))
            elif child.tag in ('file', 'resource', 'template'):
                record.files.append(file_class(
                    child.tag, child.text.strip(), child.get('to'),
                    child.get('visible')))

    # -------------------------------------------------------------------------
    @classmethod
    def xml_variables(cls, root_elt, processing, processor, with_default=True):
        """Read variable definitions in processor tree and fill ``variables``
        XML structure.

        :param root_elt: (:class:`lxml.etree.Element` instance)
            Element that linked the result.
        :param processing:
            (:class:`~ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param with_default: (boolean)
            Add default value in ``<var>``.
        """
        if not len(processing.variables):
            return

        # Browse variables
        group_elt = etree.SubElement(root_elt, 'variables')
        values = dict([(k.name, (k.value, k.default, k.visible))
                       for k in processing.variables])
        for group in processor.findall('processor/variables/group'):
            elt = group.xpath('label[@xml:lang="en"]')
            if len(elt):
                group_elt.append(
                    etree.Comment(u'{0:.^30}'.format(elt[0].text)))
            for var in group.findall('var'):
                value = values.get(var.get('name'), (None, None, False))
                elt = etree.SubElement(group_elt, 'var', name=var.get('name'))
                if value[2]:
                    elt.set('visible', 'true')
                etree.SubElement(elt, 'value').text = \
                    value[0] if value[0] is not None \
                    else (var.find('default') is not None
                          and var.find('default').text.strip()) \
                          or (var.get('type') == 'boolean' and 'false') or ''
                if with_default and value[1] is not None:
                    etree.SubElement(elt, 'default').text = value[1]

    # -------------------------------------------------------------------------
    @classmethod
    def xml_file_set(cls, root_elt, record, file_type, with_comment=True):
        """Save set of files in a XML object.

        :param root_elt: (:class:`lxml.etree.Element` instance)
            Element that linked the result.
        :param record: (:class:`~.models.projects.ProjectProcessing`
            or :class:`~.models.projects.ProjectPack` instance).
        :param file_type: ('file', 'resource' or 'template')
            File type.
        :param with_comment: (boolean, default=True)
            If ``True``, add a comment line before element.
         """
        items = [k for k in record.files if k.file_type == file_type]
        if len(items) == 0:
            return
        if with_comment:
            root_elt.append(
                etree.Comment('{0:.^32}'.format('%ss' % file_type)))
        group_elt = etree.SubElement(root_elt, '%ss' % file_type)
        for item in items:
            elt = etree.SubElement(group_elt, file_type)
            if hasattr(item, 'target') and item.target:
                elt.set('to', item.target)
            if hasattr(item, 'visible') \
                   and not (file_type == 'file' and item.visible) \
                   and not (file_type != 'file' and not item.visible):
                elt.set('visible', item.visible and 'true' or 'false')
            elt.text = item.path


# =============================================================================
class ProjectUser(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``User``."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'projects_users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer, ForeignKey('projects.project_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    user_id = Column(types.Integer, ForeignKey('users.user_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    in_menu = Column(types.Boolean(), default=False)
    perm = Column(types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'))
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, user_id, in_menu=False, perm=None):
        """Constructor method."""
        self.project_id = project_id
        self.user_id = user_id
        self.in_menu = bool(in_menu)
        if perm != 'none':
            self.perm = perm

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectUser({project_id}, {user_id}, {in_menu}, '{perm}')>" \
               .format(project_id=self.project_id or -1, user_id=self.user_id,
                       in_menu=self.in_menu, perm=self.perm)


# =============================================================================
class ProjectGroup(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``Group``."""
    # pylint: disable = I0011, W0142, R0903

    __tablename__ = 'projects_groups'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer, ForeignKey('projects.project_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    group_id = Column(types.String(ID_LEN), ForeignKey('groups.group_id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    perm = Column(types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'),
                  default='user')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, group_id, perm=None):
        """Constructor method."""
        self.project_id = project_id
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectGroup({project_id}, '{group_id}', '{perm}')>".format(
            project_id=self.project_id or -1, group_id=self.group_id,
            perm=self.perm)


# =============================================================================
class ProjectProcessing(Base):
    """SQLAlchemy-powered project processing model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'projects_processings'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(types.Integer, ForeignKey('projects.project_id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    processor = Column(types.String(ID_LEN), nullable=False)
    output = Column(types.String(PATH_LEN))
    variables = relationship('ProjectProcessingVariable')
    files = relationship('ProjectProcessingFile')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description, processor, output=None):
        """Constructor method."""
        self.project_id = project_id
        self.label = u' '.join(label.split()).strip()[0:LABEL_LEN]
        if description:
            self.description = \
                u' '.join(description.strip().split())[0:DESCRIPTION_LEN]
        self.processor = processor.strip()[0:ID_LEN]
        self.output = output and output.strip()[0:PATH_LEN] or ''

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectProcessing({project_id}, {processing_id}, '{label}',"\
               " '{processor}', '{output}')>".format(
            project_id=self.project_id or -1,
            processing_id=self.processing_id or -1, label=self.label,
            processor=self.processor, output=self.output)

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, processing_elt, check_if_exists=True):
        """Load a processing from a XML file.

        :param processing_elt: (:class:`lxml.etree.Element` instance)
            Processing XML element.
        :param check_if_exists: (boolean, default=True)
            Check if processing already exists before inserting.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        if processing_elt is None:
            return _('nothing to do!')

        label = ' '.join(processing_elt.findtext('label').strip().split())
        if check_if_exists:
            processing = DBSession.query(cls).filter_by(
                project_id=project_id, label=label).first()
            if processing is not None:
                return _('Processing "${l}" already exists.', {'l': label})

        processing = cls(
            project_id, label,
            processing_elt.findtext('description'),
            processing_elt.findtext('processor').strip(),
            processing_elt.findtext('output') is not None
                and processing_elt.findtext('output').strip() or None)
        Project.load_set(processing_elt, processing, ProjectProcessingFile)

        DBSession.add(processing)
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, processor):
        """Serialize a processing to a XML representation.

        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (:class:`lxml.etree.Element`)
        """
        proc_elt = etree.Element('processing')
        etree.SubElement(proc_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(proc_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        etree.SubElement(proc_elt, 'processor').text = self.processor
        if processor is not None:
            Project.xml_variables(proc_elt, self, processor)
        Project.xml_file_set(proc_elt, self, 'resource')
        Project.xml_file_set(proc_elt, self, 'template')
        if self.output:
            proc_elt.append(etree.Comment('{0:.^32}'.format('Output')))
            etree.SubElement(proc_elt, 'output').text = self.output

        return proc_elt


# =============================================================================
class ProjectProcessingVariable(Base):
    """SQLAlchemy-powered project processing variable model."""
    # pylint: disable = I0011, R0903, W0142

    __tablename__ = 'projects_processings_variables'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'processing_id'],
            ['projects_processings.project_id',
             'projects_processings.processing_id'],
            onupdate='CASCADE', ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    name = Column(types.String(ID_LEN), primary_key=True)
    value = Column(types.String(VALUE_LEN))
    default = Column(types.String(VALUE_LEN))
    visible = Column(types.Boolean, default=False)

    # -------------------------------------------------------------------------
    def __init__(self, name, value, default=None, visible=False):
        """Constructor method."""
        self.name = name.strip()[0:ID_LEN]
        self.value = \
            isinstance(value, basestring) and value[0:VALUE_LEN] or value
        self.default = \
            isinstance(default, basestring) and default[0:VALUE_LEN] or default
        self.visible = bool(visible)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectProcessingVariable({project_id}, {processing_id}, "\
               "'{name}', '{value}', '{default}', {visible})>".format(
            project_id=self.project_id or -1,
            processing_id=self.processing_id or -1, name=self.name,
            value=self.value, default=self.default, visible=self.visible)


# =============================================================================
class ProjectProcessingFile(Base):
    """SQLAlchemy-powered project processing file model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'projects_processings_files'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'processing_id'],
            ['projects_processings.project_id',
             'projects_processings.processing_id'],
            onupdate='CASCADE', ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    file_type = Column(types.Enum('resource', 'template',
        name='prjprcfil_type_enum'), primary_key=True)
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

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectProcessingFile({project_id}, {processing_id}, "\
               "'{file_type}', '{path}', '{target}')>".format(
            project_id=self.project_id or -1,
            processing_id=self.processing_id or -1, file_type=self.file_type,
            path=self.path, target=self.target)


# =============================================================================
class ProjectPack(Base):
    """SQLAlchemy-powered project pack model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'projects_packs'
    __table_args__ = (UniqueConstraint('project_id', 'label'),
                      {'mysql_engine': 'InnoDB'})

    project_id = Column(types.Integer, ForeignKey('projects.project_id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    recursive = Column(types.Boolean, default=False)
    files = relationship('ProjectPackFile')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, recursive=False):
        """Constructor method."""
        self.project_id = project_id
        self.label = u' '.join(label.strip().split())[0:LABEL_LEN]
        if description:
            self.description = \
                u' '.join(description.strip().split())[0:DESCRIPTION_LEN]
        self.recursive = bool(recursive)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectPack({project_id}, {pack_id}, '{label}', "\
               "{recursive})>".format(
            project_id=self.project_id or -1, pack_id=self.pack_id or -1,
            label=self.label, recursive=self.recursive).encode('utf8')

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, pack_elt):
        """Load a pack from a XML file.

        :param pack_elt: (:class:`lxml.etree.Element` instance)
            Pack XML element.
        """
        pack = cls(project_id, pack_elt.findtext('label'),
                   pack_elt.findtext('description'),
                   pack_elt.get('recursive'))
        Project.load_set(pack_elt, pack, ProjectPackFile)

        DBSession.add(pack)
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a pack to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        pack_elt = etree.Element('pack')
        if self.recursive:
            pack_elt.set('recursive', 'true')
        etree.SubElement(pack_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(pack_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 12,
                subsequent_indent=' ' * 12)
        Project.xml_file_set(pack_elt, self, 'file', False)
        Project.xml_file_set(pack_elt, self, 'resource', False,)
        Project.xml_file_set(pack_elt, self, 'template', False)

        return pack_elt


# =============================================================================
class ProjectPackFile(Base):
    """SQLAlchemy-powered project pack file model."""
    # pylint: disable = I0011, R0903

    __tablename__ = 'projects_packs_files'
    __table_args__ = (
        ForeignKeyConstraint(['project_id', 'pack_id'],
            ['projects_packs.project_id', 'projects_packs.pack_id'],
            onupdate='CASCADE', ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    file_type = Column(types.Enum('file', 'resource', 'template',
        name='prjpckfil_type_enum'), primary_key=True)
    path = Column(types.String(PATH_LEN), primary_key=True)
    target = Column(types.String(PATH_LEN))
    visible = Column(types.Boolean())

    # -------------------------------------------------------------------------
    def __init__(self, file_type, path, target=None, visible=None):
        """Constructor method."""
        self.file_type = file_type
        self.path = path.strip()[0:PATH_LEN]
        self.target = (target and target.strip()[0:PATH_LEN]) \
            or (file_type == 'template'
                and self.path.partition('/')[2][0:PATH_LEN]) or None
        self.visible = (visible is None and file_type == 'file' and True) \
                       or bool(visible)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<ProjectPackFile({project_id}, {pack_id}, '{file_type}',"\
               "'{path}', {visible}, '{target}')>".format(
            project_id=self.project_id or -1, pack_id=self.pack_id or -1,
            file_type=self.file_type, path=self.path, visible=self.visible,
            target=self.target)
