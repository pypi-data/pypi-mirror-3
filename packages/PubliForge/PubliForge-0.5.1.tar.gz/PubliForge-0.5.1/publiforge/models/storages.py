# $Id: storages.py 86b088d85a5a 2012/03/21 22:20:47 patrick $
# -*- coding: utf-8 -*-
"""SQLAlchemy-powered model definition for storages."""

from os.path import exists, join
import shutil
from lxml import etree
from textwrap import fill
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, encrypt, normalize_name
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, Base, DBSession
from .users import User
from .groups import Group


STORAGE_ACCESS = {'open': _('open'), 'restricted': _('restricted'),
                    'closed': _('closed')}
VCS_ENGINES = {'none': _(u'none – None'), 'local': _(u'local – Local'),
               'hg': u'hg – Mercurial', 'svn': u'svn – Subversion',
               'git': u'git – Git'}
STORAGE_PERMS = {'editor': _('File editor'), 'user': _('User')}
REFRESH = 3600
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Storage(Base):
    """SQLAlchemy-powered storage model."""
    # pylint: disable = I0011, W0142, R0902

    __tablename__ = 'storages'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(types.String(ID_LEN), primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    vcs_engine = Column(
        types.Enum(*VCS_ENGINES.keys(), name='vcs_engine_enum'),
        nullable=False)
    vcs_url = Column(types.String(PATH_LEN))
    vcs_user = Column(types.String(ID_LEN))
    vcs_password = Column(types.String(40))
    public_url = Column(types.String(PATH_LEN))
    access = Column(
        types.Enum(*STORAGE_ACCESS.keys(), name='stg_access_enum'),
        nullable=False, default='open')
    refresh = Column(types.Integer, default=REFRESH)
    users = relationship('StorageUser', backref='storage')
    groups = relationship('StorageGroup')

    # -------------------------------------------------------------------------
    def __init__(self, settings, storage_id, label, description=None,
                 vcs_engine='local', vcs_url=None, vcs_user=None,
                 vcs_password=None, public_url=None, access=None,
                 refresh=None):
        """Constructor method."""
        # pylint: disable = I0011, R0913
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.label = u' '.join(label.strip().split())[0:LABEL_LEN]
        if description:
            self.description = \
                u' '.join(description.strip().split())[0:DESCRIPTION_LEN]
        self.access = access
        self.vcs_engine = vcs_engine
        if not vcs_engine in ('none', 'local'):
            self.vcs_url = vcs_url[0:PATH_LEN]
            self.vcs_user = vcs_user and vcs_user.strip()[0:ID_LEN]
            self.set_vcs_password(settings, vcs_password)
        elif public_url is not None:
            self.public_url = public_url.strip()[0:PATH_LEN]
        self.refresh = refresh

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return u"<Storage('{storage_id}', '{label}', '{access}', "\
            "'{vcs_engine}', '{vcs_url}', '{vcs_user}', {refresh})>".format(
            storage_id=self.storage_id, label=self.label,
            access=self.access, vcs_engine=self.vcs_engine,
            vcs_url=self.vcs_url, vcs_user=self.vcs_user,
            refresh=self.refresh or 0).encode('utf8')

    # -------------------------------------------------------------------------
    def set_vcs_password(self, settings, vcs_password):
        """Encrypt and set password.

        :param settings: (dictionary)
            Pyramid deployment settings.
        :param vcs_password: (string)
            Clear VCS password.
        """
        if vcs_password:
            self.vcs_password = encrypt(
                vcs_password.strip(), settings['auth.key'])

    # -------------------------------------------------------------------------
    @classmethod
    def delete(cls, storage_root, storage_id):
        """Delete a storage.

        :param storage_root: (string)
            Storage root path.
        :param storage_id: (string)
            Storage identifier.
        """
        # Delete records in database
        DBSession.query(cls).filter_by(storage_id=storage_id).delete()
        DBSession.commit()

        # Remove directory
        if exists(join(storage_root, storage_id)):
            shutil.rmtree(join(storage_root, storage_id))

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, settings, storage_elt, error_if_exists=True):
        """Load a storage from a XML file.

        :param settings: (dictionary)
            Application settings.
        :param storage_elt: (:class:`lxml.etree.Element` instance)
            Storage XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if storage already exists.
        :return: (:class:`pyramid.i18n.TranslationString` ``None`` or
            :class:`Storage` instance)
            Error message or ``None`` or the new storage object.
        """
        # Reset
        storage_id = storage_elt.get('%sid' % XML_NS).strip()[0:ID_LEN]
        label = u' '.join(
            storage_elt.findtext('label').strip().split())[0:LABEL_LEN]
        if storage_elt.find('reset') is not None \
               and bool(storage_elt.findtext('reset')):
            Storage.delete(settings['storage.root'], storage_id)

        # Check if already exists
        storage = DBSession.query(cls).filter_by(
            storage_id=storage_id).first()
        if storage is None:
            storage = DBSession.query(cls).filter_by(label=label).first()
        if storage is not None:
            if error_if_exists:
                return _(
                    'Storage "${i}" already exists.', {'i': storage_id})
            return

        # Create storage
        # pylint: disable = I0011, W0142
        vcs_elt = storage_elt.find('vcs')
        record = {
            'label': label,
            'description': storage_elt.findtext('description'),
            'vcs_engine': vcs_elt.get('engine'),
            'vcs_url': vcs_elt.findtext('url') is not None
                and vcs_elt.findtext('url').strip() or None,
            'vcs_user': vcs_elt.findtext('user') is not None
                and vcs_elt.findtext('user').strip() or None,
            'vcs_password': vcs_elt.findtext('password') is not None
                and vcs_elt.findtext('password').strip() or None,
            'public_url': vcs_elt.findtext('public') is not None
                and vcs_elt.findtext('public').strip() or None,
            'access': storage_elt.findtext('access') is not None
                and storage_elt.findtext('access').strip() or 'open',
            'refresh': storage_elt.findtext('refresh') is not None
                and int(storage_elt.findtext('refresh').strip()) or None}
        storage = Storage(settings, storage_id, **record)
        DBSession.add(storage)
        DBSession.commit()

        # Add users
        done = []
        for item in storage_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if login not in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    storage.users.append(StorageUser(
                        storage.storage_id, user.user_id,
                        item.get('in-menu'), item.get('permission', 'user')))
                done.append(login)

        # Add groups
        done = []
        for item in storage_elt.findall('members/member-group'):
            group_id = normalize_name(item.text)[0:ID_LEN]
            if group_id not in done:
                group = DBSession.query(Group).filter_by(
                    group_id=group_id).first()
                if group is not None:
                    storage.groups.append(StorageGroup(storage.storage_id,
                        group.group_id, item.get('permission', 'user')))
                done.append(group_id)

        DBSession.commit()
        return storage

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a storage to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        storage_elt = etree.Element('storage')
        storage_elt.set('%sid' % XML_NS, self.storage_id)
        etree.SubElement(storage_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(storage_elt, 'description').text = fill(
                self.description, initial_indent='\n' + ' ' * 8,
                subsequent_indent=' ' * 8)
        elt = etree.SubElement(storage_elt, 'vcs')
        elt.set('engine', self.vcs_engine)
        if self.vcs_url:
            etree.SubElement(elt, 'url').text = self.vcs_url
        if self.vcs_user:
            etree.SubElement(elt, 'user').text = self.vcs_user
        if self.public_url:
            etree.SubElement(elt, 'public').text = self.public_url
        if self.access != 'open':
            etree.SubElement(storage_elt, 'access').text = self.access
        if self.refresh != REFRESH:
            etree.SubElement(storage_elt, 'refresh').text = str(self.refresh)

        # Members
        if self.users or self.groups:
            members_elt = etree.SubElement(storage_elt, 'members')
            for user in self.users:
                elt = etree.SubElement(members_elt, 'member')
                elt.text = user.user.login
                if user.in_menu:
                    elt.set('in-menu', 'true')
                if user.perm != 'user':
                    elt.set('permission', user.perm or 'none')
            for group in self.groups:
                elt = etree.SubElement(members_elt, 'member-group')
                elt.text = group.group_id
                if group.perm != 'user':
                    elt.set('permission', group.perm)

        return storage_elt


# =============================================================================
class StorageUser(Base):
    """SQLAlchemy-powered association table between ``Storage`` and
    ``User``."""
    # pylint: disable = I0011, R0913, W0142

    __tablename__ = 'storages_users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(types.String(ID_LEN), ForeignKey(
        'storages.storage_id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True)
    user_id = Column(types.Integer, ForeignKey('users.user_id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    in_menu = Column(types.Boolean(), default=False)
    perm = Column(types.Enum(*STORAGE_PERMS.keys(), name='stg_perms_enum'))
    vcs_user = Column(types.String(ID_LEN))
    vcs_password = Column(types.String(40))
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, storage_id, user_id, in_menu=False, perm=None,
                 vcs_user=None, vcs_password=None, settings=None):
        """Constructor method."""
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.user_id = user_id
        self.in_menu = bool(in_menu)
        if perm != 'none':
            self.perm = perm
        if vcs_user and settings is not None:
            self.vcs_user = vcs_user
            self.set_vcs_password(settings, vcs_password)

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<StorageUser('{storage_id}', {user_id}, {in_menu}, "\
               "'{perm}', '{vcs_user}')>".format(
            storage_id=self.storage_id, user_id=self.user_id,
            in_menu=self.in_menu, perm=self.perm, vcs_user=self.vcs_user or '')

    # -------------------------------------------------------------------------
    def set_vcs_password(self, settings, vcs_password):
        """Encrypt and set VCS password.

        :param settings: (dictionary)
            Pyramid deployment settings.
        :param password: (string)
            Clear password.
        """
        self.vcs_password = encrypt(vcs_password, settings['auth.key'])


# =============================================================================
class StorageGroup(Base):
    """SQLAlchemy-powered association table between ``Storage`` and
    ``Group``."""
    # pylint: disable = I0011, W0142, R0903

    __tablename__ = 'storages_groups'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(types.String(ID_LEN), ForeignKey(
        'storages.storage_id', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True)
    group_id = Column(types.String(ID_LEN), ForeignKey('groups.group_id',
        onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    perm = Column(types.Enum(*STORAGE_PERMS.keys(), name='stg_perms_enum'),
                  default='user')

    # -------------------------------------------------------------------------
    def __init__(self, storage_id, group_id, perm=None):
        """Constructor method."""
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<StorageGroup('{storage_id}', '{group_id}', '{perm}')>".format(
            storage_id=self.storage_id, group_id=self.group_id, perm=self.perm)
