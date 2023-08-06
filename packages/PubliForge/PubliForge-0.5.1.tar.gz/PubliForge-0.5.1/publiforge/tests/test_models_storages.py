# $Id: test_models_storages.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``models.storages`` classes."""

import unittest
from tempfile import mkdtemp

from ..tests import ModelTestCase


# =============================================================================
class UnitTestModelsStoragesStorage(ModelTestCase):
    """Unit test class for ``models.storages.Storage``."""
    # pylint: disable = I0011, C0103, R0904

    _key = 'seekrit'
    _storage_id = '_test_storage'
    _storage_root = mkdtemp()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from os.path import exists
        from shutil import rmtree
        from ..models.storages import Storage
        if self.session.query(Storage)\
               .filter_by(storage_id=self._storage_id).first() is not None:
            Storage.delete(self._storage_root, self._storage_id)
        self.session.commit()
        if exists(self._storage_root):
            rmtree(self._storage_root)
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make an ``Storage`` object."""
        from ..models.storages import Storage
        return Storage(
            {'auth.key': self._key}, self._storage_id, 'Test storage')

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.storages.Storage.__init__]"""
        from ..models.storages import Storage
        storage1 = self._make_one()
        self.session.add(storage1)
        self.session.commit()
        storage2 = self.session.query(Storage)\
                     .filter_by(storage_id=storage1.storage_id).first()
        self.assertNotEqual(storage2, None)
        self.assertEqual(storage2.storage_id, storage1.storage_id)
        self.assertEqual(storage2.access, storage1.access)
        self.assertEqual(storage2.vcs_engine, storage1.vcs_engine)
        self.assertEqual(storage2.refresh, storage1.refresh)

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.storages.Storage.__repr__]"""
        storage = self._make_one()
        info = repr(storage)
        self.assertTrue('<Storage(' in info)
        self.assertTrue("'%s'" % storage.storage_id in info)
        self.assertTrue("'%s'" % storage.access in info)
        self.assertTrue("'%s'" % storage.vcs_engine in info)
        self.assertTrue(str(storage.refresh) in info)

    # -------------------------------------------------------------------------
    def test_delete(self):
        """[u:models.storages.Storage.delete]"""
        from os.path import exists, join
        from ..models.storages import Storage
        storage = self._make_one()
        storage_id = storage.storage_id
        self.session.add(storage)
        self.session.commit()
        storage.delete(self._storage_root, storage.storage_id)
        self.session.commit()
        storage = self.session.query(Storage)\
                    .filter_by(storage_id=storage_id).first()
        self.assertEqual(storage, None)
        self.assertFalse(exists(join(self._storage_root, storage_id)))


# =============================================================================
class UnitTestModelsStoragesStorageUser(unittest.TestCase):
    """Unit test class for ``models.storages.StorageUser``."""

    _key = 'seekrit'
    _storage_id = '_test_storage'
    _user_id = 1000

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``StorageUser`` object."""
        from ..models.storages import StorageUser
        return StorageUser(
            self._storage_id, self._user_id, True, 'user', 'user1',
            'sesame', {'auth.key': self._key})

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.storages.StorageUser.__init__]"""
        from ..lib.utils import encrypt
        storage_user = self._make_one()
        self.assertEqual(storage_user.user_id, self._user_id)
        self.assertTrue(storage_user.in_menu)
        self.assertEqual(storage_user.perm, 'user')
        self.assertEqual(storage_user.vcs_user, 'user1')
        self.assertEqual(
            storage_user.vcs_password, encrypt('sesame', self._key))

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.storages.StorageUser.__repr__]"""
        storage_user = self._make_one()
        info = repr(storage_user)
        self.assertTrue('<StorageUser(' in info)
        self.assertTrue('%s' % storage_user.storage_id in info)
        self.assertTrue('%s' % storage_user.user_id in info)


# =============================================================================
class IntegrationTestModelsStorages(ModelTestCase):
    """Integration test class for ``models.storages``."""
    # pylint: disable = I0011, C0103

    _key = 'seekrit'
    _user_id = 1000
    _storage_id = '_test_storage'
    _storage_root = mkdtemp()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from os.path import exists
        from shutil import rmtree
        from ..models.users import User
        from ..models.storages import Storage
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        if self.session.query(Storage)\
               .filter_by(storage_id=self._storage_id).first() is not None:
            Storage.delete(self._storage_root, self._storage_id)
        self.session.commit()
        if exists(self._storage_root):
            rmtree(self._storage_root)
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_storage(self):
        """Make a ``Storage`` object."""
        # pylint: disable = I0011, E1101
        from ..models.storages import Storage
        return Storage(
            {'auth.key': self._key}, self._storage_id, 'Test storage')

    # -------------------------------------------------------------------------
    def _make_user(self):
        """Make an ``User`` object."""
        from ..models.users import User
        user = User({'auth.key': self._key}, '_test_user', status='active',
                    password='mypassword', name=u'Gédéon TEUSEMANIE',
                    email='test@prismallia.fr', lang='en')
        user.user_id = self._user_id
        return user

    # -------------------------------------------------------------------------
    def test_delete_user(self):
        """[i:models.storages] remove user"""
        from ..models.users import User
        from ..models.storages import StorageUser
        storage = self._make_storage()
        user = self._make_user()
        self.session.add(user)
        storage.users.append(
            StorageUser(self._storage_id, self._user_id))
        self.session.add(storage)
        self.session.commit()
        self.assertEqual(len(storage.users), 1)
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        self.session.commit()
        self.assertEqual(len(storage.users), 0)
