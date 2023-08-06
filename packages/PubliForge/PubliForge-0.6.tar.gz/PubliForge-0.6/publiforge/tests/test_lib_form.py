# $Id: test_lib_form.py 0badce09f183 2012/03/14 09:14:17 patrick $
# pylint: disable = I0011, R0904
"""Tests of ``lib.form`` classes and functions."""

import unittest
from pyramid import testing


# =============================================================================
class UnitTestLibFormButton(unittest.TestCase):
    """Unit test class for ``lib.form.button``."""

    # -------------------------------------------------------------------------
    def test_with_no_label(self):
        """[u:lib.form.button] with no label"""
        from ..lib.form import button
        from webhelpers.html import literal
        test_button = button(url='url', src='src')
        expected_result = \
            literal(u'<a href="url"><img src="src" alt="None"/></a> ')
        self.assertEqual(test_button, expected_result)

    # -------------------------------------------------------------------------
    def test_regular_button(self):
        """[u:lib.form.button] regular button"""
        from ..lib.form import button
        from webhelpers.html import literal
        test_button = \
            button(url='url', label='label',
                       src='src', title='title', class_='value')
        expected_result = \
            literal(u'<a href="url" title="title" class="value">'
                    '<img src="src" alt="label"/>label</a> ')
        self.assertEqual(test_button, expected_result)


# =============================================================================
class UnitTestLibFormValidate(unittest.TestCase):
    """Unit test class for ``lib.form.validate``."""

    # -------------------------------------------------------------------------
    def test_validate_request_no_post(self):
        """[u:lib.form.validate] request with no post"""
        from ..lib.form import Form
        request = testing.DummyRequest()
        form = Form(request)
        self.assertTrue(len(request.POST) == 0)
        self.assertFalse(form.validate())


# =============================================================================
class UnitTestLibFormBegin(unittest.TestCase):
    """Unit test class for ``lib.form.begin``."""

    # -------------------------------------------------------------------------
    def test_begin_unsecure_form(self):
        """[u:lib.form.begin] unsecure form  """
        from ..lib.form import Form
        from webhelpers.html import literal
        request = testing.DummyRequest()
        form = Form(request)
        form._secure = False
        html = form.begin(url='url')
        expected_html = literal(u'<form action="url" method="post">')
        self.assertEqual(html, expected_html)

    # -------------------------------------------------------------------------
    def test_begin_secure_form(self):
        """[u:lib.form.begin] secure form  """
        from ..lib.form import Form
        from webhelpers.html import literal
        request = testing.DummyRequest()
        form = Form(request)
        form._secure = True
        html = form.begin(url='url')
        expected_html = \
            literal('<form action="url" method="post"><div><input id="_csrf"'
                    ' name="_csrf" type="hidden" value="%s" /></div>'
                    % request.session.new_csrf_token())
        self.assertEqual(html, expected_html)
