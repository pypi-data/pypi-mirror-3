# $Id: file.py ada86c3ea608 2012/03/22 22:52:47 patrick $
# pylint: disable = I0011, C0322
"""File view callables."""

from os import sep
from os.path import join, isdir, splitext, relpath
from subprocess import Popen, PIPE
from colander import Mapping, SchemaNode, String, Boolean

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.response import Response
from pyramid.i18n import get_localizer

from ..lib.utils import _, EXCLUDED_FILES, FILE_TYPES, TEXT_TYPES
from ..lib.utils import get_mime_type, age
from ..lib.views import get_action, current_storage, file_download
from ..lib.views import create_pack, add2container
from ..lib.form import Form
from ..lib.renderer import Paging
from ..models import close_dbsession


# =============================================================================
class FileView(object):
    """Class to manage files in a storage."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='file_search',
                 renderer='../Templates/fil_search.pt',
                 permission='stg.read')
    def search(self):
        """Search file in storages."""
        # Scope
        scope = []
        storage_ids = []
        session = self._request.session
        route = self._request.route_path('storage_root', storage_id='')
        for item in session['menu']:
            for subitem in item[3] or ():
                if subitem[1] and subitem[1].startswith(route):
                    scope.append((subitem[1][len(route):], subitem[0]))
                    storage_ids.append(subitem[1][len(route):])
        if 'storage' in session \
               and not session['storage']['storage_id'] in storage_ids:
            scope.insert(0, (session['storage']['storage_id'],
                              session['storage']['label']))
            storage_ids.append(session['storage']['storage_id'])

        # Form & results
        form = self._search_form(storage_ids)
        results = None
        if form.validate():
            results = self._search(form.values)
        elif 'search' in session:
            results = session['search'][1]

        # Action
        action, items = get_action(self._request)
        if action[0:4] == 'dnl!':
            return file_download(self._request,
                self._request.registry.settings['storage.root'], items,
                get_localizer(self._request).translate(_('search')))
        elif action == 'cls!' and 'container' in session:
            del session['container']
        elif action[0:4] in ('pck!', 'prc!'):
            add2container(self._request, action[0:3], action[4:7], '.', items)
            form.forget('#')
        elif action[0:4] == 'npk!' and 'project' in self._request.session:
            items = create_pack(self._request, items)
            if items[0] is not None:
                return HTTPFound(self._request.route_path(
                    'pack_edit', project_id=items[0], pack_id=items[1]))

        self._request.breadcrumbs.add(_('Advanced search'))
        return {
            'form': form, 'scope': scope, 'FILE_TYPES': FILE_TYPES,
            'results': results}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_info',
                 renderer='../Templates/fil_info.pt',
                 permission='stg.read')
    def info(self):
        """Show file information and VCS log."""
        storage, handler = current_storage(self._request)
        path = self._request.matchdict['path']
        filename = path[-1]
        path = '/'.join(path[:-1])
        fullname = join(handler.vcs.path, path, filename).encode('utf8')
        if self._request.params.get('page_size'):
            self._request.session['page_size'] = \
                int(self._request.params['page_size'])
        log = handler.vcs.log(path, filename,
            int(self._request.session.get('page_size', 20)))

        content = None
        action = get_action(self._request)[0]
        if action[0:4] == 'shw!':
            action = action[4:]
            content = handler.vcs.revision(fullname, action)
            if content is None:
                self._request.session.flash(_('Unable to retrieve this '
                    'revision: it was probably moved.'), 'alert')
            else:
                content = {'route': 'file_revision', 'revision': action,
                    'file': content.decode('utf8'),
                    'label': _('Revision ${r}:', {'r': action})}
        elif action[0:4] == 'dif!':
            action = action[4:]
            content = handler.vcs.diff(fullname, action)
            content = {
                'route': 'file_diff', 'revision': action, 'file': content,
                'label': _('Differences with revision ${r}:', {'r': action})}

        self._request.breadcrumbs.add(_('File information'))
        return {
            'form': Form(self._request), 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'TEXT_TYPES': TEXT_TYPES, 'FILE_TYPES': FILE_TYPES, 'log': log,
            'age': age, 'page_sizes': Paging.page_sizes, 'content': content}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_download', permission='stg.read')
    def download(self):
        """Download a file."""
        storage = current_storage(self._request)[0]
        path = self._request.matchdict['path']
        real_path = join(self._request.registry.settings['storage.root'],
                         storage['storage_id'], *path[0:-1])
        if not isdir(real_path):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        return file_download(self._request, real_path, (path[-1],))

    # -------------------------------------------------------------------------
    @view_config(route_name='file_revision', permission='stg.read')
    def revision(self):
        """Retrieve a revision of a file."""
        handler, filename, fullname, revision = self._current_file()
        content = handler.vcs.revision(fullname, revision)

        if content is None:
            self._request.session.flash(_('Unable to retrieve this revision:'
                ' it was probably moved.'), 'alert')
            return HTTPFound(self._request.route_path(
                'file_info', storage_id=handler.uid,
                path='/'.join(self._request.matchdict['path'])))

        download_name = u'%s.r%s%s' % (
            splitext(filename)[0], revision, splitext(filename)[1])
        response = Response(content, content_type=get_mime_type(fullname)[0])
        response.headerlist.append(('Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    @view_config(route_name='file_diff', permission='stg.read')
    def diff(self):
        """Differences between a version and current version."""
        handler, filename, fullname, revision = self._current_file()
        content = handler.vcs.diff(fullname, revision)

        download_name = u'%s.r%s.diff' % (splitext(filename)[0], revision)
        response = Response(content, content_type='text/x-diff')
        response.headerlist.append(('Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    def _current_file(self):
        """Return handler, filename, fullname, and revision."""
        handler = current_storage(self._request)[1]

        # pylint: disable = I0011, W0142
        path = self._request.matchdict['path']
        revision = self._request.matchdict['revision']
        fullname = handler.vcs.full_path(*path)
        if fullname is None or isdir(fullname):
            raise HTTPForbidden()

        return handler, path[-1], fullname, revision

    # -------------------------------------------------------------------------
    def _search_form(self, storage_ids):
        """Return a search form.

        :param storage_ids: (list)
            Available storage IDs.
        :return: (:class:`~.lib.form.Form` instance)
        """
        # Schema
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(String(), name='files', missing=None))
        schema.add(SchemaNode(String(), name='words', missing=None))
        for sid in storage_ids:
            schema.add(SchemaNode(Boolean(), name='~%s' % sid, missing=False))

        # Defaults
        defaults = {}
        if 'search' in self._request.session:
            defaults = self._request.session['search'][0]
        elif 'storage' in self._request.session:
            defaults = {'~%s' %
                self._request.session['storage']['storage_id']: True}

        return Form(self._request, schema=schema, defaults=defaults)

    # -------------------------------------------------------------------------
    def _search(self, criteria):
        """Search files in storages and return a result.

        :param criteria: (dictionary)
            Search criteria.
        :return: (list)
            A list of tuples such as ``(score, file_type, storage_id,
            path)``.

        This method stores criteria and results in ``session['search']``.
        """
        if not criteria['files'] and not criteria['words']:
            self._request.session.flash(_('Define search criteria!'), 'alert')
            return

        # Search in storages
        found = False
        results = []
        for storage_id in criteria:
            if storage_id[0] == '~' and criteria[storage_id]:
                found = True
                results += self._search_storage(
                    storage_id[1:], criteria['files'], criteria['words'])

        if not found:
            self._request.session.flash(_('Select a storage!'), 'alert')
            return

        self._request.session['search'] = (criteria, results)
        return results

    # -------------------------------------------------------------------------
    def _search_storage(self, storage_id, files, words):
        """Search files in one storage.

        :param storage_id: (string)
            Id of storage.
        :param files: (string)
            Query on files.
        :param words: (string)
            Words to search.
        :return: (list)
            See :meth:`_search`
        """
        root = join(
            self._request.registry.settings['storage.root'], storage_id)

        # Query by file name
        results1 = self._search_storage_by_filename(root, files)
        if results1 is not None and not results1:
            return results1

        # Query by word
        results2 = self._search_storage_by_word(root, words)
        if results1:
            results2 = set(results1) & set(results2)

        # Complete
        results1 = []
        for item in results2:
            results1.append((100, get_mime_type(item)[1],
                             storage_id, relpath(item, root)))
        return results1

    # -------------------------------------------------------------------------
    @classmethod
    def _search_storage_by_filename(cls, root, files):
        """Search files by file name.

        :param root: (string)
            Root path.
        :param files: (string)
            Query on files.
        :return: (list or ``None``)
        """
        if files is None or not files.strip():
            return

        excluded = set(EXCLUDED_FILES)
        results = []
        files = files.split()
        cmd = ['find', root, '-type', 'f', '-name',  files[0]]
        for item in files[1:]:
            cmd += ['-or', '-name', item]

        for item in Popen(cmd, stdout=PIPE).communicate()[0].split('\n'):
            item = item.strip().decode('utf8')
            if item and excluded.isdisjoint(set(item.split(sep))):
                results.append(item)

        return results

    # -------------------------------------------------------------------------
    @classmethod
    def _search_storage_by_word(cls, root, words):
        """Search files by word in it.

        :param root: (string)
            Root path.
        :param words: (string)
            Words to search.
        :return: (list or ``None``)
        """
        if words is None or not words.strip():
            return

        excluded = set(EXCLUDED_FILES)
        results = {}
        words = words.split()
        for item in words:
            cmd = ['find', root, '-type', 'f',
                   '-exec', 'grep', '-l', item, '{}', ';']
            files = Popen(cmd, stdout=PIPE).communicate()[0].split('\n')
            files = [k.strip().decode('utf8') for k in files if k.strip()]
            if not results:
                for item in files:
                    if excluded.isdisjoint(set(item.split(sep))):
                        results[item] = None
            else:
                for item in results.keys():
                    if not item in files:
                        del results[item]
            if not results:
                break

        return results.keys()
