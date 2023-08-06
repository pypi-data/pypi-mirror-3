# $Id: test_models_users.py df43b426606b 2012/03/09 15:58:44 yvon $
# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``models.users`` classes."""

import unittest

from pyramid import testing

from ..tests import ModelTestCase


# =============================================================================
class UnitTestModelsUsersUser(ModelTestCase):
    """Unit test class for ``models.users.User``."""
    # pylint: disable = I0011, C0103, R0904

    _key = 'seekrit'
    _password = 'mypassword'

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.users import User
        self.session.query(User).filter(
            User.login.like('_test_%')).delete('fetch')
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make an ``User`` object."""
        from ..models.users import User
        return User({'auth.key': self._key}, '_test_user', status='active',
                    password=self._password, name=u'Félicie TASSION',
                    email='test@prismallia.fr', lang='en')

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.users.User.__init__]"""
        from ..models.users import User
        from datetime import datetime
        from ..lib.utils import hash_sha
        user1 = self._make_one()
        self.session.add(user1)
        self.session.commit()
        user2 = self.session.query(User).filter_by(login=user1.login).first()
        self.assertNotEqual(user2, None)
        self.assertEqual(user2.login, user1.login)
        self.assertEqual(user2.status, user1.status)
        self.assertEqual(user2.password, hash_sha(self._password, self._key))
        self.assertEqual(user2.name, user1.name)
        self.assertEqual(user2.email, user1.email)
        self.assertEqual(user2.lang, user1.lang)
        self.assertTrue(user2.created <= datetime.now())
        self.assertTrue(user2.created == user2.updated)

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.users.User.__repr__]"""
        user = self._make_one()
        info = repr(user)
        self.assertTrue('<User(' in info)
        self.assertTrue('-1' in info)
        self.assertTrue('%s' % user.login in info)
        self.assertTrue('%s' % user.status in info)
        self.assertTrue('%s' % user.name.encode('utf8') in info)
        self.assertTrue('%s' % user.lang in info)

    # -------------------------------------------------------------------------
    def test_set_password(self):
        """[u:models.users.User.set_password]"""
        from ..lib.utils import hash_sha
        user = self._make_one()
        password = user.password
        user.set_password({'auth.key': self._key}, 'foo')
        self.assertNotEqual(user.password, password)
        self.assertEqual(user.password, hash_sha('foo', self._key))

    # -------------------------------------------------------------------------
    def test_setup_environment(self):
        """[u:models.users.User.setup_environment]"""
        request = testing.DummyRequest()
        request.registry.settings['auth.key'] = self._key
        request.registry.settings['available_languages'] = 'fr en'
        user = self._make_one()
        user.setup_environment(request)
        self.assertTrue('user_id' in request.session)
        self.assertEqual(request.session['user_id'], user.user_id)
        self.assertTrue('name' in request.session)
        self.assertEqual(request.session['name'], user.name)
        self.assertTrue('paging' in request.session)
        self.assertEqual(request.session['paging'][0], user.page_size)
        self.assertTrue('home' in request.session)
        self.assertEqual(request.session['home'], user.home)


# =============================================================================
class UnitTestModelsUsersUserPerm(unittest.TestCase):
    """Unit test class for ``models.users.UserPerm``."""

    _user_id = 1000

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``UserPerm`` object."""
        from ..models.users import UserPerm
        return UserPerm(self._user_id, 'usr', 'manager')

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.users.UserPerm.__init__]"""
        user_perm = self._make_one()
        self.assertEqual(user_perm.scope, 'usr')
        self.assertEqual(user_perm.level, 'manager')

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.users.UserPerm.__repr__]"""
        user_perm = self._make_one()
        info = repr(user_perm)
        self.assertTrue('<UserPerm(' in info)
        self.assertTrue(str(self._user_id) in info)
        self.assertTrue("'%s'" % user_perm.scope in info)
        self.assertTrue("'%s'" % user_perm.level in info)


# =============================================================================
class UnitTestModelsUsersUserIP(unittest.TestCase):
    """Unit test class for ``models.users.UserIP``."""

    _user_id = 1000

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make an ``UserIP`` object."""
        from ..models.users import UserIP
        return UserIP(self._user_id, '192.168.0.1')

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.users.UserIP.__init__]"""
        user_ip = self._make_one()
        self.assertEqual(user_ip.ip, '192.168.0.1')

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.users.UserIP.__repr__]"""
        user_ip = self._make_one()
        info = repr(user_ip)
        self.assertTrue('<UserIP(' in info)
        self.assertTrue(str(self._user_id) in info)
        self.assertTrue('%s' % user_ip.ip in info)


# =============================================================================
class IntegrationTestModelsUsers(ModelTestCase):
    """Integration test class for ``models.users``."""
    # pylint: disable = I0011, C0103

    _user_id = 1000

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.users import User
        self.session.query(User).filter(
            User.login.like('_test_%')).delete('fetch')
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_user(self):
        """Make an ``User`` object."""
        # pylint: disable = I0011, E1101
        from ..models.users import User
        user = User({'auth.key': 'seekrit'}, '_test_user', status='active',
                    password='mypassword', name=u'Gérard MENVUSSA',
                    email='test@prismallia.fr', lang='en')
        user.user_id = self._user_id
        return user

    # -------------------------------------------------------------------------
    def test_delete_cascade_ip(self):
        """[i:models.users.User] delete, cascade IP"""
        # pylint: disable = I0011, W0104
        from ..models.users import User, UserIP
        user = self._make_user()
        user.ips.append(UserIP(user.user_id, '192.168.0.1'))
        self.session.add(user)
        self.session.commit()
        user_id = user.user_id
        user_ip = self.session.query(UserIP).filter_by(user_id=user_id).first()
        self.assertNotEqual(user_ip, None)
        self.assertEqual(user_ip.ip, '192.168.0.1')
        self.session.query(User).filter_by(user_id=user_id).delete()
        self.session.commit()
        user_ip = self.session.query(UserIP).filter_by(user_id=user_id).first()
        self.assertEqual(user_ip, None)
