# $Id: test_views_security.py ffe4e2582c93 2011/12/18 21:51:32 patrick $
# pylint: disable = I0011, R0904
"""Tests of ``views.security`` functions."""

from ..tests import FunctionalTestCase


# =============================================================================
class FunctionalTestViewsSecurityLogin(FunctionalTestCase):
    """Functional test class for ``views.security.login``."""
    # pylint: disable = I0011, C0103, R0904

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(FunctionalTestViewsSecurityLogin, self).__init__(method_name)
        self._csrf = None

    # -------------------------------------------------------------------------
    def setUp(self):
        """Set up test application."""
        FunctionalTestCase.setUp(self)
        response = self.testapp.get('/login')
        self._csrf = response.form.get('_csrf').value

    # -------------------------------------------------------------------------
    def test_empty_password(self):
        """[f:views.security.login] empty password."""
        params = {'_csrf': self._csrf, 'login': 'user1', 'password': None}
        response = self.testapp.post('/login', params, status=200)
        self.assertTrue('class="error"' in response)

    # -------------------------------------------------------------------------
    def test_wrong_password(self):
        """[f:views.security.login] wrong password."""
        params = {'_csrf': self._csrf, 'login': 'user1',
                  'password': '12345678'}
        response = self.testapp.post('/login', params, status=200)
        self.assertTrue('"flashAlert"' in response)
        self.assertTrue('incorrect' in response)

    # -------------------------------------------------------------------------
    def test_inactive(self):
        """[f:views.security.login] inactive account."""
        params = {'_csrf': self._csrf, 'login': 'test1',
                  'password': 'test1pwd'}
        response = self.testapp.post('/login', params, status=200)
        self.assertTrue('"flashAlert"' in response)
        self.assertTrue('activ' in response)

    # -------------------------------------------------------------------------
    def test_expired(self):
        """[f:views.security.login] inactive expired."""
        params = {'_csrf': self._csrf, 'login': 'test3',
                  'password': 'test3pwd'}
        response = self.testapp.post('/login', params, status=200)
        self.assertTrue('"flashAlert"' in response)
        self.assertTrue('expir' in response)

    # -------------------------------------------------------------------------
    def test_authorized(self):
        """[f:views.security.login] authorized user."""
        from datetime import datetime, timedelta
        from ..models import DBSession
        from ..models.users import User
        params = {'_csrf': self._csrf, 'login': 'user1',
                  'password': 'user1pwd'}
        self.testapp.post('/login', params, status=302)
        user = DBSession.query(User).filter_by(login=params['login']).first()
        self.assertNotEqual(user, None)
        self.assertTrue(
            user.last_login > datetime.now() - timedelta(minutes=1))
