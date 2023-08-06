# $Id: test_models_groups.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
# -*- coding: utf-8 -*-
# pylint: disable = I0011, R0904
"""Tests of ``models.groups`` classes."""

import unittest

from ..tests import ModelTestCase


# =============================================================================
class UnitTestModelsGroupsGroup(ModelTestCase):
    """Unit test class for ``models.groups.Group``."""
    # pylint: disable = I0011, C0103

    _group_id = '_test_group'

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.groups import Group
        self.session.query(Group)\
            .filter_by(group_id=self._group_id).delete()
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``Group`` object."""
        from ..models.groups import Group
        group = Group(self._group_id, u'Les éditeurs', u"Un groupe d'éditeurs")
        return group

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.groups.Group.__init__]"""
        from ..models.groups import Group
        group1 = self._make_one()
        self.session.add(group1)
        self.session.commit()
        group2 = self.session.query(Group)\
                     .filter_by(group_id=group1.group_id).first()
        self.assertNotEqual(group2, None)
        self.assertEqual(group2.group_id, group1.group_id)
        self.assertEqual(group2.label, group1.label)
        self.assertEqual(group2.description, group1.description)

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.groups.Group.__repr__]"""
        group = self._make_one()
        info = repr(group)
        self.assertTrue('<Group(' in info)
        self.assertTrue("'%s'" % self._group_id in info)
        self.assertTrue("'%s'" % group.label.encode('utf8') in info)


# =============================================================================
class UnitTestModelsGroupsGroupPerm(unittest.TestCase):
    """Unit test class for ``models.groups.GroupPerm``."""

    _group_id = '_test_group'

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``GroupPerm`` object."""
        from ..models.groups import GroupPerm
        return GroupPerm(self._group_id, 'usr', 'manager')

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.groups.GroupPerm.__init__]"""
        group_perm = self._make_one()
        self.assertEqual(group_perm.scope, 'usr')
        self.assertEqual(group_perm.level, 'manager')

    # -------------------------------------------------------------------------
    def test_repr(self):
        """[u:models.groups.GroupPerm.__repr__]"""
        group_perm = self._make_one()
        info = repr(group_perm)
        self.assertTrue('<GroupPerm(' in info)
        self.assertTrue("'%s'" % self._group_id in info)
        self.assertTrue("'%s'" % group_perm.scope in info)
        self.assertTrue("'%s'" % group_perm.level in info)


# =============================================================================
class IntegrationTestModelsGroups(ModelTestCase):
    """Integration test class for ``models.groups``."""
    # pylint: disable = I0011, C0103

    _user_id = 2000
    _group_id = '_test_group'

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.users import User
        from ..models.groups import Group
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        self.session.query(Group).filter_by(group_id=self._group_id).delete()
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_group(self):
        """Make a ``Group`` object."""
        # pylint: disable = I0011, E1101
        from ..models.groups import Group
        group = Group(self._group_id, u'Les éditeurs', u"Un groupe d'éditeurs")
        return group

    # -------------------------------------------------------------------------
    def _make_user(self):
        """Make an ``User`` object."""
        from ..models.users import User
        user = User({'auth.key': 'seekrit'}, '_test_user', status='active',
                    password='mypassword', name=u'Félicie TASSION',
                    email='test@prismallia.fr', lang='en')
        user.user_id = self._user_id
        return user

    # -------------------------------------------------------------------------
    def test_delete_cascade_perm(self):
        """[i:models.groups] delete, cascade permission"""
        from ..models.groups import Group, GroupPerm
        group = self._make_group()
        group.perms.append(GroupPerm(self._group_id, 'usr', 'manager'))
        self.session.add(group)
        self.session.commit()
        group_perm = self.session.query(GroupPerm)\
            .filter_by(group_id=self._group_id).first()
        self.assertNotEqual(group_perm, None)
        self.assertEqual(group_perm.scope, 'usr')
        self.assertEqual(group_perm.level, 'manager')
        self.session.query(Group)\
            .filter_by(group_id=self._group_id).delete('fetch')
        self.session.commit()
        group_perm = self.session.query(GroupPerm)\
            .filter_by(group_id=self._group_id).first()
        self.assertEqual(group_perm, None)

    # -------------------------------------------------------------------------
    def test_remove_user(self):
        """[i:models.groups] remove user"""
        from ..models.groups import Group
        user = self._make_user()
        group = self._make_group()
        group.users.append(user)
        self.session.add(user)
        self.session.add(group)
        self.session.commit()
        group = self.session.query(Group)\
                .filter_by(group_id=self._group_id).first()
        self.assertEqual(len(group.users), 1)
        del group.users[0]
        self.session.commit()
        group = self.session.query(Group)\
                .filter_by(group_id=self._group_id).first()
        self.assertEqual(len(group.users), 0)

    # -------------------------------------------------------------------------
    def test_delete_user(self):
        """[i:models.groups] delete user"""
        from ..models.users import User
        user = self._make_user()
        self.session.add(user)
        group = self._make_group()
        group.users.append(user)
        self.session.add(group)
        self.session.commit()
        self.session.query(User)\
            .filter_by(user_id=self._user_id).delete()
        self.session.commit()
        self.assertEqual(len(group.users), 0)
