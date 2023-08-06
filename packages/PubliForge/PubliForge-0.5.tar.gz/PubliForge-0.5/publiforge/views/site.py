# $Id: site.py 87b7d52fda37 2012/02/23 17:08:44 patrick $
# pylint: disable = I0011, C0322
"""Site view callables."""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden

from ..lib.xml import upload_configuration, export_configuration
from ..lib.utils import _, has_permission
from ..lib.views import get_action
from ..lib.form import Form
from ..models import DBSession, close_dbsession
from ..models.users import User
from ..models.groups import Group
from ..models.storages import Storage
from ..models.processors import Processor
from ..models.projects import Project


# =============================================================================
class SiteView(object):
    """Class to manage global website."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='site_admin', renderer='../Templates/sit_admin.pt',
                 permission='sit.adm')
    def admin(self):
        """List users, groups, storages, processors and projects and allow
        import/export operations."""

        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'admin')
            action = ''
        elif action[0:4] == 'exp!':
            return self._export_site(items)

        fbuild = self._request.registry['fbuild']
        fbuild.refresh_agent_list(self._request)

        quantity = {'users': DBSession.query(User).count(),
                    'groups': DBSession.query(Group).count(),
                    'storages': DBSession.query(Storage).count(),
                    'projects': DBSession.query(Project).count()}

        self._request.breadcrumbs.add(_('Site administration'), 2)
        return {
            'form': Form(self._request), 'action': action,
            'db': (DBSession.bind.name, DBSession.bind.url.database),
            'agents': fbuild.agent_list(),
            'processor_labels': sorted(Processor.labels(self._request)),
            'quantity': quantity}

    # -------------------------------------------------------------------------
    def _export_site(self, objects):

        """Export site.
        :param objects: (list)
            List of objects to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        if not has_permission(self._request, 'admin'):
            raise HTTPForbidden()

        elements = []
        for obj in objects:
            if obj == 'users':
                for user in DBSession.query(User):
                    elements.append(user.xml(True))
            elif obj == 'groups':
                for group in DBSession.query(Group):
                    elements.append(group.xml())
            elif obj == 'storages':
                for storage in DBSession.query(Storage):
                    elements.append(storage.xml())
            elif obj == 'projects':
                for project in DBSession.query(Project):
                    elements.append(project.xml(self._request))

        name = self._request.registry.settings.get('skin.label', 'publiforge')
        if len(objects) == 1:
            name = '%s_%s.pf%s' % (name, objects[0], objects[0][0])
        else:
            name = '%s.pf' % name
        return export_configuration(elements, name)
