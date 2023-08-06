# $Id: test_views_project.py bc236c725df4 2012/01/24 22:50:00 patrick $
# pylint: disable = I0011, R0904
"""Tests of ``views.project`` functions."""

from ..tests import ModelTestCase, FunctionalTestCase


# =============================================================================
class UnitTestViewsProjectProjectView(ModelTestCase):
    """Unit test class for ``views.project.Project``."""

    # -------------------------------------------------------------------------
    def test_admin(self):
        """[u:views.project.admin]"""
        from ..views.project import ProjectView
        from ..lib.renderer import Paging
        from ..lib.form import Form
        self.config.add_route('site_admin', '/site/admin')
        result = ProjectView(self._make_request()).admin()
        self.assertTrue('form' in result)
        self.assertTrue(isinstance(result['form'], Form))
        self.assertTrue('paging' in result)
        self.assertTrue(isinstance(result['paging'], Paging))
        self.assertTrue('project_status' in result)
        self.assertTrue('active' in result['project_status'])


# =============================================================================
class FunctionalTestViewProjectView(FunctionalTestCase):
    """Functional test class for ``views.project.Project``."""

    # -------------------------------------------------------------------------
    def test_not_authenticated(self):
        """[f:views.project.admin] not authenticated."""
        response = self.testapp.get('/project/admin', status=302)
        self.assertEqual(response.location,
                         'http://localhost/login?came_from=%2Fproject%2Fadmin')

    # -------------------------------------------------------------------------
    def test_not_authorized(self):
        """[f:views.project.admin] not authorized."""
        self.testapp.login('user3')
        self.testapp.get('/project/admin', status=403)

    # -------------------------------------------------------------------------
    def test_authorized(self):
        """[f:views.project.admin] authorized."""
        self.testapp.login('user1')
        self.testapp.get('/project/admin', status=200)
