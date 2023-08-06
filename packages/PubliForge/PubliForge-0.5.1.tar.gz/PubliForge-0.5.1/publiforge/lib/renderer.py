# $Id: renderer.py ada86c3ea608 2012/03/22 22:52:47 patrick $
# -*- coding: utf-8 -*-
"""Renderer functions."""

import webhelpers.paginate as paginate
from webhelpers.html import literal, HTML, tags

from pyramid.i18n import get_localizer

from ..lib.utils import _, has_permission
from ..models import DBSession
from ..models.users import PAGE_SIZE
from ..models.storages import Storage, StorageUser
from ..models.projects import Project, ProjectUser


# =============================================================================
def sortable_column(request, label, sort, current_sorting=None,
                    paging_id=None):
    """Output a header of column with `sort up` and `sort down` buttons.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param label: (string)
         Label of column.
    :param sort: (string)
         Sort criteria.
    :param current_sorting: (string, optional)
        Default current sorting.
    :param paging_id: (string, optional)
        Paging ID.
    :return: (literal HTML string)
    """
    img = '/Static/Images/sort_%s.png'
    current = request.params.get('sort') or current_sorting
    query_string = {}
    if request.GET:
        query_string.update(request.GET)
    if paging_id:
        query_string.update({'paging_id': paging_id})

    query_string['sort'] = '+%s' % sort
    url = request.current_route_path(_query=query_string)
    xhtml = '+%s' % sort == current and tags.image(img % 'down_off', 'Down')\
            or HTML.a(tags.image(img % 'down', 'Down'), href=url)

    query_string['sort'] = '-%s' % sort
    url = request.current_route_path(_query=query_string)
    xhtml += '-%s' % sort == current and tags.image(img % 'up_off', 'Up')\
             or HTML.a(tags.image(img % 'up', 'Up'), href=url)

    return literal('%s %s' % (label, xhtml))


# =============================================================================
class Breadcrumbs(object):
    """User breadcrumb trail, current title page and back URL management.

    This class uses session and stores its history in
    ``session['breadcrumbs']``. It is a list of crumbs. Each crumb is a tuple
    such as ``(<title>, <route_name>, <route_parts>)``
    """

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request

    # -------------------------------------------------------------------------
    def current_title(self):
        """Title of current page."""
        session = self._request.session
        return ('breadcrumbs' in session and len(session['breadcrumbs']) > 0
                and session['breadcrumbs'][-1][0]) or ''

    # -------------------------------------------------------------------------
    def current_path(self):
        """Path of current page."""
        if not 'breadcrumbs' in self._request.session:
            return self._request.route_path('home')
        crumb = self._request.session['breadcrumbs'][-1]
        return self._request.route_path(crumb[1], **crumb[2])

    # -------------------------------------------------------------------------
    def trail(self):
        """Output XHTML breadcrumb trail."""
        if not 'breadcrumbs' in self._request.session \
               or len(self._request.session['breadcrumbs']) < 2:
            return literal('&nbsp;')

        translate = get_localizer(self._request).translate
        crumbs = []
        for crumb in self._request.session['breadcrumbs'][0:-1]:
            if crumb[1] is not None:
                crumbs.append(u'<a href="%s">%s</a>' % (
                    self._request.route_path(crumb[1], **crumb[2]),
                    translate(crumb[0])))
            else:
                crumbs.append(translate(crumb[0]))
        return literal(u' » '.join(crumbs))

    # -------------------------------------------------------------------------
    def back_title(self):
        """Output title of previous page."""
        if not 'breadcrumbs' in self._request.session \
               or len(self._request.session['breadcrumbs']) < 2:
            return _('home')
        return get_localizer(self._request).translate(
            self._request.session['breadcrumbs'][-2][0])

    # -------------------------------------------------------------------------
    def back_button(self):
        """A button to return to the previous page."""
        return literal(
            u'<a href="{url}" title="{title}">'
            '<img src="/Static/Images/back.png" alt="Back"/></a>'.format(
                url=self.back_path(), title=self.back_title()))

    # -------------------------------------------------------------------------
    def back_path(self):
        """Output the path of previous page."""
        if not 'breadcrumbs' in self._request.session \
               or len(self._request.session['breadcrumbs']) < 2:
            return self._request.route_path('home')
        crumb = self._request.session['breadcrumbs'][-2]
        return self._request.route_path(crumb[1], **crumb[2])

    # -------------------------------------------------------------------------
    def add(self, title, length=6, root_chunks=6, replace=None):
        """Add a crumb in breadcrumb trail.

        :param title: (string)
            Page title in breadcrumb trail.
        :param length: (int, default=6)
            Maximum crumb number. If 0, it keeps the current length.
        :param root_chunks: (int, default=6)
            Number of path chunks to compare to highlight menu item.
        :param replace: (string, optional):
            If current path is ``replace``, this method call :meth:`pop` before
            any action.
        """
        # Environment
        session = self._request.session
        if not 'breadcrumbs' in session:
            session['breadcrumbs'] = [(_('Home'), 'home', {}, 1)]
        if not length:
            length = len(session['breadcrumbs'])

        # Replace
        if replace and self.current_path() == replace:
            self.pop()

        # Scan old breadcrumb trail to find the right position
        route_name = (self._request.matched_route
                      and self._request.matched_route.name)
        if route_name is None:
            return
        compare_name = route_name.replace('_root', '_browse')
        crumbs = []
        for crumb in session['breadcrumbs']:
            if len(crumbs) >= length - 1 or not crumb[1] \
                   or crumb[1].replace('_root', '_browse') == compare_name:
                break
            crumbs.append(crumb)

        # Add new breadcrumb
        crumbs.append((
            title, route_name, self._request.matchdict, root_chunks))
        session['breadcrumbs'] = crumbs

    # -------------------------------------------------------------------------
    def pop(self):
        """Pop last breadcrumb."""
        session = self._request.session
        if 'breadcrumbs' in session and len(session['breadcrumbs']) > 1:
            session['breadcrumbs'] = session['breadcrumbs'][0:-1]


# =============================================================================
class Menu(object):
    """User menu management."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request
        self._translate = get_localizer(request).translate

    # -------------------------------------------------------------------------
    def xhtml(self):
        """Output XHTML user menu."""
        if not 'user_id' in self._request.session:
            return ''
        if 'menu' in self._request.session:
            return self._make_xhtml()
        menu = []

        # Storages
        if has_permission(self._request, 'stg_user'):
            submenu = [self._entry(_('Advanced search'), 'file_search'),
                       self._entry(_('All storages'), 'storage_index')]
            self._storage_entries(self._request.session['user_id'], submenu)
            menu.append(self._entry(_('Storages'), None, submenu))

        # Projects
        if has_permission(self._request, 'prj_user'):
            submenu = [self._entry(_('All projects'), 'project_index')]
            self._project_entries(self._request.session['user_id'], submenu)
            menu.append(self._entry(_('Projects'), None, submenu))

        # Administration
        submenu = []
        if has_permission(self._request, 'admin'):
            submenu.append(self._entry(_('Site'), 'site_admin'))
        if has_permission(self._request, 'usr_editor'):
            submenu.append(self._entry(_('Users'), 'user_admin'))
        if has_permission(self._request, 'grp_editor'):
            submenu.append(self._entry(_('Groups'), 'group_admin'))
        if has_permission(self._request, 'stg_editor'):
            submenu.append(self._entry(_('Storages'), 'storage_admin'))
        if has_permission(self._request, 'prj_editor'):
            submenu.append(self._entry(_('Projects'), 'project_admin'))
        if submenu:
            menu.append(self._entry(_('Administration'), None, submenu))

        if not menu:
            return ''
        self._request.session['menu'] = tuple(menu)
        return self._make_xhtml()

    # -------------------------------------------------------------------------
    def _make_xhtml(self):
        """Return an <ul> structure with current highlighted current entry."""
        # Make XHTML
        menu = self._request.session['menu']
        xhtml = '<ul>%s</ul>' % self._make_xhtml_entries(menu, 0)

        # Highlight current entry
        if 'breadcrumbs' in self._request.session:
            for crumb in reversed(self._request.session['breadcrumbs'][1:]):
                if crumb[1] is None:
                    continue
                path = self._request.route_path(crumb[1], **crumb[2])
                path = '/'.join(path.split('/')[0:crumb[3] + 1])\
                       .replace('/edit/', '/view/')
                if 'href="%s"' % path in xhtml:
                    xhtml = xhtml.replace('<a class="slow" href="%s"' % path,
                        '<a class="slow current" href="%s"' % path)
                    break

        # Tag current project
        if 'project' in  self._request.session:
            path = self._request.route_path('project_dashboard',
                project_id=self._request.session['project']['project_id'],
                _query={'id': self._request.session['project']['project_id']})
            xhtml = xhtml.replace('<li><a class="slow" href="%s"' % path,
                '<li class="active"><a class="slow" href="%s"' % path)

        return literal(xhtml)

    # -------------------------------------------------------------------------
    def _make_xhtml_entries(self, entries, depth):
        """Return <li> tags with entries.

        :param entries: (tuple)
            Tuple of entry tuples (See :meth:`_entry`)
        :param depth: (integer)
            Depth of entries in menu.
        """
        xhtml = ''
        for entry in entries:
            tag = (depth == 0 and '<strong>') \
                  or (depth == 1 and entry[2] and '<em>') or ''
            xhtml += '<li>' \
                + (entry[1] and '<a class="slow" href="%s">' % entry[1] or '')\
                + tag + entry[0] + tag.replace('<', '</') \
                + (entry[1] and '</a>' or '')
            if entry[3]:
                xhtml += '<ul>%s</ul>' % self._make_xhtml_entries(
                    entry[3], depth + 1)
            xhtml += '</li>'
        return xhtml

    # -------------------------------------------------------------------------
    def _storage_entries(self, user_id, submenu):
        """Update menu entries for user storages shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        # Look for user storages
        for storage in DBSession.query(Storage).join(StorageUser)\
                .filter(StorageUser.user_id == user_id)\
                .filter(StorageUser.in_menu == True).order_by(Storage.label):
            submenu.append(self._entry(
                storage.label, 'storage_root',
                None, True, storage_id=storage.storage_id))

    # -------------------------------------------------------------------------
    def _project_entries(self, user_id, submenu):
        """Update menu entries for user projects shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        # Look for user projects
        for project in DBSession\
                .query(Project.project_id, Project.label, ProjectUser.perm)\
                .join(ProjectUser).filter(ProjectUser.user_id == user_id)\
                .filter(ProjectUser.in_menu == True).order_by(Project.label):
            pid = project[0]
            subentries = [
                self._entry(_('Dashboard'), 'project_dashboard',
                            None, True, project_id=pid),
                self._entry(_('Last results'), 'project_results',
                            None, True, project_id=pid)]
            if project[2] == 'editor' \
                   or has_permission(self._request, 'prj_editor'):
                subentries.append(self._entry(_('Settings'), 'project_view',
                    None, True, project_id=pid))
            submenu.append(self._entry(project[1], 'project_dashboard',
                tuple(subentries), True, project_id=pid, _query={'id': pid}))

    # -------------------------------------------------------------------------
    def _entry(self, label, route_name, subentries=None, is_minor=False,
               **kwargs):
        """A menu entry tuple.

        :param label: (string)
            Label of the entry.
        :param route_name: (string)
            Name of the route for the link.
        :param subentries: (list, optional)
            List of subentries.
        :param is_minor: (boolean, default=False)
            Indicate whether this entry is a minor one.
        :param kwargs: (dictionary)
            Keyworded arguments for :meth:`pyramid.request.Request.route_path`.
        :return: (tuple)
            A tuple such as
            ``(label, url, is_minor, (subentry, subentry...))``.
        """
        return (self._translate(label),
                route_name and self._request.route_path(route_name, **kwargs),
                is_minor, subentries and tuple(subentries))


# =============================================================================
class Paging(paginate.Page):
    """An extended :class:`webhelpers.paginate.Page` that manages one page of a
    splitted list or results from ORM queries.

    This class uses three parameters in request: ``page_size`` and ``page``.

    It stores its information and filters definitions in ``session['paging']``.
    This structure looks like:

    ``session['paging'] = (default_page_size, {'users': {'size': 20, 'page': 3,
    'sort': 'name', 'f_id': 'smith', 'f_group': 'managers',...},...})``
    """

    page_sizes = ('', 5, 10, 20, 40, 80, 160, 320)

    # -------------------------------------------------------------------------
    def __init__(self, request, paging_id, collection, **kwargs):
        """Constructor method."""
        self.paging_id = paging_id
        self._request = request

        # Update paging session
        params = request.session['paging'][1][paging_id]
        if request.params.get('page_size'):
            params['size'] = int(request.params['page_size'])
        if request.params.get('page'):
            params['page'] = int(request.params['page'])

        # Return page
        get_params = self._request.GET.copy()
        get_params.update({'paging_id': paging_id})
        super(Paging, self).__init__(
            collection, params['page'], params['size'],
            url=paginate.PageURL(self._request.path, get_params), **kwargs)

    # -------------------------------------------------------------------------
    @classmethod
    def params(cls, request, paging_id, default_sorting):
        """Return current paging parameters: filter criteria and sorting.

        :param paging_id: (string)
            Paging ID.
        :param default_sorting: (string)
            Default sorting.
        :return: (dictionary)
            The paging dictionary. See :class:`~.renderer.Paging` class.
        """
        if not 'paging' in request.session:
            request.session['paging'] = (PAGE_SIZE, {})
        if not paging_id in request.session['paging'][1]:
            request.session['paging'][1][paging_id] = {
                'size': request.session['paging'][0],
                'page': 1, 'sort': default_sorting}
        if len(request.POST):
            params = request.session['paging'][1][paging_id]
            request.session['paging'][1][paging_id] = {
                'size': params['size'], 'page': params['page'],
                'sort': params['sort']}

        params = request.session['paging'][1][paging_id]
        for key in request.params:
            if (key[0:2] == 'f_' or key == 'sort') and request.params[key]:
                params[key] = request.params[key]

        return params

    # -------------------------------------------------------------------------
    def pager_top(self, icon_name=None, label=None):
        """Output a string with links to first, previous, next and last pages.

        :param icon_name: (string, optional)
            Name of the icon representing the items.
        :param label: (string, optional)
            Label representing the items.
        :return: (string)
        """
        icon = ''
        if icon_name is not None and label is not None:
            icon = literal('<img src="/Static/Images/{i}.png" alt="{l}"'
                        ' title="{l}"/>  &nbsp;'.format(i=icon_name, l=label))
        img = '<img src="/Static/Images/go_%s.png" alt="%s"/>'
        return icon + self.pager('$link_first $link_previous '
            '<span>$first_item &ndash; $last_item</span> / $item_count '
            '$link_next $link_last',
            symbol_first=literal(img % ('first', 'First')),
            symbol_previous=literal(img % ('previous', 'Previous')),
            symbol_next=literal(img % ('next', 'Next')),
            symbol_last=literal(img % ('last', 'Last'))) or literal('&nbsp;')

    # -------------------------------------------------------------------------
    def pager_bottom(self, icon_name=None, label=None):
        """Output a string with links to some previous and next pages.

        :param icon_name: (string, optional)
            URL of the icon representing the items.
        :param label: (string, optional)
            Label representing the items.
        :return: (string)
        """
        icon = ''
        if icon_name is not None and label is not None:
            icon = literal('<img src="/Static/Images/{i}.png" alt="{l}"'
                       ' title="{l}"/> &nbsp;'.format(i=icon_name, l=label))
        return (icon + self.pager('~3~')) or literal('&nbsp;')

    # -------------------------------------------------------------------------
    def sortable_column(self, label, sort):
        """Output a header of column with `sort up` and `sort down` buttons.

        See :func:`~.lib.utils.sortable_column`.

        :param label: (string)
             Label of column.
        :param sort: (string)
             Sort criteria.
        :return: (literal HTML string)
        """
        return sortable_column(self._request, label, sort,
            self._request.session['paging'][1][self.paging_id]['sort'],
            self.paging_id)

    # -------------------------------------------------------------------------
    @classmethod
    def pipe(cls):
        """Output a pipe image."""
        return literal(
            '<img src="/Static/Images/action_pipe.png" alt="Pipe"/>')


# =============================================================================
class TabSet(object):
    """A class to manages tabs."""

    # -------------------------------------------------------------------------
    def __init__(self, request, labels):
        """Constructor method."""
        self._request = request
        self.labels = labels

    # -------------------------------------------------------------------------
    def toc(self, tab_id):
        """Output a table of content of the ``TabSet`` in an ``<ul>``
        structure.

        :param tab_id: (string)
            Tab set ID.
        :return: (string)
            ``<ul>`` structure.
        """
        translate = get_localizer(self._request).translate
        xml = '<ul id="%s" class="tabToc">\n' % tab_id
        for index, label in enumerate(self.labels):
            xml += '  <li><a class="tabLink" id="tabLink%d" href="#tab%d">' \
                   '<span>%s</span></a></li>\n' % (
                index, index, translate(label))
        xml += '</ul>\n'
        return literal(xml)

    # -------------------------------------------------------------------------
    def tab_begin(self, index, access_key=None):
        """Open a tab zone.

        :param index: (integer)
            Tab index.
        :param access_key: (string, optional)
            Access key for tab.
        :return: (string)
            Opening ``fieldset`` structure with legend.
        """
        return literal('<fieldset class="tabContent" id="tab%d">\n'
                       '  <legend%s><span>%s</span></legend>\n' % (
            index, access_key and ' accesskey="%s"' % access_key or '',
            self.labels[index]))

    # -------------------------------------------------------------------------
    @classmethod
    def tab_end(cls):
        """Close a tab zone."""
        return literal('</fieldset>')
