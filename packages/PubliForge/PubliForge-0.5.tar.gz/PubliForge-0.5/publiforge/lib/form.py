# $Id: form.py bc236c725df4 2012/01/24 22:50:00 patrick $
"""Form validation and rendering library."""

import colander
from webhelpers.html import tags, HTML, literal

from pyramid.httpexceptions import HTTPNotAcceptable
from pyramid.i18n import get_localizer

from ..lib.utils import _


# =============================================================================
class SameAs(object):
    # pylint: disable = I0011, R0903
    """This class implements a ``colander`` validator to check if to fields are
    identical."""

    # -------------------------------------------------------------------------
    def __init__(self, request, reference):
        """Constructor method."""
        self.request = request
        self.reference = reference

    # -------------------------------------------------------------------------
    def __call__(self, node, value):
        """This method raises a :class:`colander.Invalid` instance as an
        exception value is not same as ``self.reference``.

        :param node: (:class:`colander.SchemaNode` instance)
        :param value: (cstruct object)
        """
        if self.request.params.get(self.reference) != value:
            raise colander.Invalid(node, _('The two fields are not identical'))


# =============================================================================
def button(url, label='', src=None, title=None, class_='button'):
    """Output a link on a label and an image with a button aspect.

    :param url: (string)
        Target URL.
    :param label: (string, optional)
        Label for roll over and ``alt``.
    :param src: (string, optional)
        Image path.
    :param title: (string, optional)
        Label for roll over.
    :param class_: (string, default='button')
        The class attribute.
    :return: (string)
        HTML tag.
    """
    if class_ == 'button' and not label and src:
        class_ = None
    return literal(u'<a href="{url}"{title}{class_}>{img}{label}</a> '\
        .format(url=url, title=title and ' title="%s"' % title or '',
        class_=class_ and ' class="%s"' % class_ or '',
        img=src and '<img src="%s" alt="%s"/>' % (src, label or title)
        or '', label=label))


# =============================================================================
def grid_item(name, label, content, required=False, hint=None, error=None,
              class_=None, tag='div'):
    """Display an item with label, hint and error message.

    :param name: (string)
        Content ID.
    :param label: (string)
        Label.
    :param content: (string)
        HTML content.
    :param required: (boolean, default=False)
        Indicate if this field is required.
    :param hint: (string, optional)
        Help message.
    :param error: (string, optional)
        Error message.
    :param class_: (string, optional)
        The class attribute.
    :param tag: (string, default='div')
        Tag which contains content, hint and error message.
    :return: (string)

    This ouputs a structure such as:

    .. code-block:: html

        <div class="[class_]">
          <label for="[name]"><em>[label]<strong>*</strong></em></label>
          <tag>
            [content]
            <em>[hint]</em>
            <strong class="error">[form.error(name)]</strong>
          </tag>
          <div class="clear"></div>
        </div>

    If ``class_`` is an empty string, ``'formItem'`` is used.
    """
    # pylint: disable = I0011, R0913
    if not content:
        return ''
    if class_ == '':
        class_ = 'formItem'
    return (literal('<div%s>' % (class_ and ' class="%s"' % class_ or ''))
        + literal('<label%s><em>' % (name and ' for="%s"' % name or ''))
        + label + (HTML.strong('*') if required else '')
        + literal('</em></label><%s>' % tag)
        + (content or literal('&nbsp;'))
        + (HTML.em(' %s' % hint) if hint else '')
        + (HTML.strong(' %s' % error, class_='error') if error else '')
        + literal('</%s><div class="clear"></div></div>' % tag))


# =============================================================================
class Form(object):
    """Form validation class."""
    # pylint: disable = I0011, R0904

    # -------------------------------------------------------------------------
    def __init__(self, request, schema=None, defaults=None, secure=True,
                 obj=None):
        """Constructor method."""
        self.values = not len(request.POST) and defaults or {}
        self._request = request
        self._schema = schema
        self._secure = secure
        self._errors = {}
        self._special = [[], '']
        self._validated = False
        if not len(request.POST) and obj is not None and schema is not None:
            for field in [k.name for k in schema]:
                if hasattr(obj, field.encode('utf8')):
                    self.values[field] = getattr(obj, field)

    # -------------------------------------------------------------------------
    def validate(self, obj=None):
        """Check if the form is validated.

        :param obj: (object, optional)
            Object to fill
        :return: (boolean)
             ``True`` if validated.
        """
        # Something to do?
        if len(self._request.POST) == 0:
            return False
        if self._validated:
            return len(self._errors) == 0

        # Cross-site request forgery protection
        if self._secure and self._request.POST.get('_csrf') \
               != self._request.session.get_csrf_token():
            raise HTTPNotAcceptable()

        # Schema validation
        params = dict(self._request.POST.items())
        if self._schema:
            try:
                self.values = self._schema.deserialize(params)
            except colander.Invalid, err:
                self._errors = {}
                for child in err.children:
                    self._errors[child.node.name] = child.messages()
        else:
            self.values.update(params)

        # Fill object
        if obj is not None and len(self._errors) == 0:
            for field in self.values:
                if hasattr(obj, field.encode('utf8')):
                    setattr(obj, field, self.values[field])

        self._validated = True
        return len(self._errors) == 0

    # -------------------------------------------------------------------------
    def has_error(self, name=None):
        """Return ``True`` if field ``name`` has an error.

        :param name: (string, optional)
            Input ID.
        :return: (boolean)
        """
        return (name is None and bool(self._errors)) or name in self._errors

    # -------------------------------------------------------------------------
    def error(self, name):
        """Return error message for field ``name``.

        :param name: (string)
            Input ID.
        :return: (string)
            Translated error message.
        """
        if not name in self._errors:
            return ''
        translate = get_localizer(self._request).translate
        return ' ; '.join([translate(error) for error in self._errors[name]])

    # -------------------------------------------------------------------------
    def static(self, name):
        """The field ``name`` will not be updated by the form."""
        if name not in self._special[0]:
            self._special[0].append(name)

    # -------------------------------------------------------------------------
    def forget(self, prefix):
        """Fields beginning by ``prefix`` are forgotten when the page is
        refreshed."""
        self._special[1] = prefix[0]

    # -------------------------------------------------------------------------
    def begin(self, url=None, method='post', multipart=False, **attrs):
        """Ouput the ``<form>`` tag.

        :param url: (string, optional)
            URL to submit form, by default, the current URL.
        :param method: (string, default='post')
            The method to use when submitting the form.
        :param multipart: (boolean, default=False)
            If set to ``True``, the enctype is set to ``multipart/form-data``.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        html = tags.form(
            url or self._request.path_qs, method, multipart, **attrs)
        if self._secure:
            token = self._request.session.get_csrf_token() \
                    or self._request.session.new_csrf_token()
            html += HTML.div(self.hidden('_csrf', token))
        return html

    # -------------------------------------------------------------------------
    @classmethod
    def end(cls):
        """Ouput the ``</form>`` tag."""
        return tags.end_form()

    # -------------------------------------------------------------------------
    @classmethod
    def submit(cls, name, label=None, class_='button', **attrs):
        """Output a submit button with the label as the caption.

        :param name: (string)
            Input ID.
        :param label: (string, optional)
            Button caption.
        :param class_: (string, default='button')
            The class attribute.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        return tags.submit(name, label, class_=class_, **attrs)

    # -------------------------------------------------------------------------
    @classmethod
    def submit_image(cls, name, label, src, class_=None):
        """Output an image submit button.

        :param name: (string)
            Input ID.
        :param label: (string)
            Label for roll over and ``alt``.
        :param src: (string)
            Image path.
        :param class_: (string, optional)
            The class attribute.
        :return: (string)
            HTML tag.
        """
        label = label.replace('"', "'")
        return literal(
            u'<input type="image" name="{name}" src="{src}" title="{label}"'
            ' alt="{label}"{class_}/>'.format(name=name, src=src, label=label,
            class_=class_ and ' class="%s"' % class_ or ''))

    # -------------------------------------------------------------------------
    @classmethod
    def submit_cancel(cls, label):
        """Output a cancel submit button.

        :param label: (string)
            Label for roll over and ``alt``.
        :return: (string)
            HTML tag.
        """
        label = label.replace('"', "'")
        return literal(
            u'<input type="image" name="ccl!" '
            'src="/Static/Images/action_cancel.png" title="{label}" '
            'alt="{label}"/>'.format(label=label))

    # -------------------------------------------------------------------------
    @classmethod
    def button(cls, url, label='', src=None, title=None, class_='button'):
        """Output a link on a label and an image with a button aspect.

        See :func:`button`.
        """
        return button(url, label, src, title, class_)

    # -------------------------------------------------------------------------
    @classmethod
    def grid_item(cls, name, label, content, required=False, hint=None,
                  error=None, class_=None, tag='div'):
        """Output an item with label, hint and error messag.

        See :func:`grid_item`.
        """
        # pylint: disable = I0011, R0913
        return grid_item(
            name, label, content, required, hint, error, class_, tag)

    # -------------------------------------------------------------------------
    def hidden(self, name, value=None, **attrs):
        """Output a hidden field.

        :param name: (string)
            Input ID.
        :param value: (string, optional)
            Hidden value.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        return tags.hidden(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def text(self, name, value=None, **attrs):
        """Output a standard text field.

        :param name: (string)
            Input ID.
        :param value: (string, optional)
            Default value.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        return tags.text(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def password(self, name, value=None, **attrs):
        """Output a password field.

        This method takes the same options as text().
        """
        return tags.password(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def checkbox(self, name, value='1', checked=False, label=None, **attrs):
        """Output a check box.

        :param name: (string)
            Input ID.
        :param value: (string, default='1')
            The value to return to the application if the box is checked.
        :param checked: (boolean, default=False)
            ``True`` if the box should be initially checked.
        :param label: (string, optional)
            A text label to display to the right of the box.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        return tags.checkbox(
            name, value, self._value(name, checked), label, **attrs)

    # -------------------------------------------------------------------------
    def select(self, name, selected_values, options, autosubmit=False,
               **attrs):
        """Output a dropdown selection box.

        :param name: (string)
            Input ID.
        :param selected_value: (string or list)
            A string or list of strings or integers giving the value(s) that
            should be preselected.
        :param options: (list of strings, integers or ``(value, label)`` pairs)
            The label will be shown on the form; the option will be returned to
            the application if that option is chosen. If you pass a ``string``
            or ``int`` instead of a ``2-tuple``, it will be used for both the
            value and the label.
        :param autosubmit: (boolean, default=False)
            If ``True``, it adds ``onchange="submit()"`` attribute.
        :param attrs: (dictionary)
            Keyworded arguments for ``webhelpers.html.tags`` object.
        :return: (string)
            HTML tag.
        """
        if isinstance(options[0], tuple):
            translate = get_localizer(self._request).translate
            opts = [(opt[0], translate(opt[1])) for opt in options]
        else:
            opts = options
        return tags.select(name, self._value(name, selected_values), opts,
                    onchange='submit()' if autosubmit else None, **attrs)

    # -------------------------------------------------------------------------
    def upload(self, name, value=None, **attrs):
        """Output a file upload field.

        :param name: (string)
            Input ID.
        :param value: (string, optional)
            Default value.
        :return: (string)
            HTML tag.
        """
        return tags.file(name, self._value(name, value), **attrs)

    # -------------------------------------------------------------------------
    def grid_text(self, name, label, required=False, hint=None, class_=''):
        """Output a standard text field in a CSS grid layout.

        :param name: (string)
            Input ID.
        :param label: (string)
            Label.
        :param required: (boolean, default=False)
            Indicate if this field is required.
        :param hint: (string, optional)
            Help message.
        :param class_: (string, optional)
            The class attribute.
        :return: (string)
            Output a grid layout.
        """
        return self.grid_item(name, label, self.text(name), required, hint,
                              self.error(name), class_)

    # -------------------------------------------------------------------------
    def grid_password(self, name, label, required=False, hint=None, class_=''):
        """Output a password field in a CSS grid layout.

        This method takes the same options as grid_text().
        """
        return self.grid_item(name, label, self.password(name), required, hint,
                              self.error(name), class_)

    # -------------------------------------------------------------------------
    def grid_checkbox(self, name, label, required=False, hint=None, class_=''):
        """Output a check box in a CSS grid layout.

        :param name: (string)
            Input ID.
        :param label: (string)
            Label.
        :param required: (boolean, default=False)
            Indicate if this field is required.
        :param hint: (string, optional)
            Help message.
        :param class_: (string, optional)
            The class attribute.
        :return: (string)
            Output a grid layout.
        """
        return self.grid_item(name, label, self.checkbox(name), required, hint,
                              self.error(name), class_, tag='span')

    # -------------------------------------------------------------------------
    def grid_select(self, name, label, options, autosubmit=False,
                    required=False, hint=None, class_=''):
        """Output a dropdown selection box in a CSS grid layout.

        :param name: (string)
            Input ID.
        :param label: (string)
            Label.
        :param options: (list of strings, integers or ``(value, label)`` pairs)
            Values in the dropdown list.
        :param autosubmit: (boolean, default=False)
            If ``True``, it adds ``onchange="submit()"`` attribute.
        :param required: (boolean, default=False)
            Indicate if this field is required.
        :param hint: (string, optional)
            Help message.
        :param class_: (string, optional)
            The class attribute.
        :return: (string)
            Output a grid layout.
        """
        # pylint: disable = I0011,R0913
        return self.grid_item(
            name, label, self.select(name, None, options, autosubmit),
            required, hint, self.error(name), class_)

    # -------------------------------------------------------------------------
    def grid_upload(self, name, label, required=False, hint=None, class_=''):
        """Output a file upload field in a CSS grid layout.

        :param name: (string)
            Input ID.
        :param label: (string)
            Label.
        :param required: (boolean, default=False)
            Indicate if this field is required.
        :param hint: (string, optional)
            Help message.
        :param class_: (string, optional)
            The class attribute.
        :return: (string)
            Output a grid layout.
        """
        return self.grid_item(name, label, self.upload(name), required, hint,
                              self.error(name), class_)

    # -------------------------------------------------------------------------
    def _value(self, name, default=None):
        """Return the best value for the field ``name``.

        :param name: (string)
            Input ID.
        :param default: (string, optional)
            Default value.
        """
        return (name not in self._special[0] and name[0] != self._special[1]
            and name in self._request.params and self._request.params[name]) \
            or (name in self.values and self.values[name]) or default
