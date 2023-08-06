# $Id: front.py ada86c3ea608 2012/03/22 22:52:47 patrick $
"""Front build management.

A *front* is a web site.
"""
# pylint: disable = I0011, C0302

import logging
import xmlrpclib
from time import time, sleep
from random import randint
from threading import Thread
from os import walk, makedirs, rename
from os.path import join, exists, isfile, dirname, relpath, normpath
from cStringIO import StringIO
from lxml import etree
import re

from pyramid.i18n import get_localizer

from ..utils import _, localizer, copy_content, decrypt
from ..utils import camel_case, has_permission, EXCLUDED_FILES
from ..rsync import get_block_size
from ..rsync import SigFile, PatchedFile, DeltaFile
from ...views import xmlrpc
from ...models import DBSession
from ...models.users import User
from ...models.processors import Processor
from ...models.storages import Storage, StorageUser


LOG = logging.getLogger(__name__)


# =============================================================================
class FrontBuildManager(object):
    """This class manages front builds.

    One instance of :class:`FrontBuildManager` is created during application
    initialization. It is only used in front mode. It is stored in application
    registry.

    ``self._agents`` is a dictionary such as ``{url: (password, weight,
    processor_list, processor_expire_time),... }`` which stores agent features.

    ``self._builds`` is a dictionary of :class:`FrontBuild` objects.

    ``self._results`` is a dictionary of dictionaries such as ``{build_id:
    result_dict}``. ``result_dict`` is a dictionary with following keys:
    ``status``, ``log``, ``expire``, ``project_id``, ``user_id``. According to
    build events, it can also contains ``files``, ``values`` and ``error``
    keys.

    ``self._results[build_id]['status']`` is one of the following strings:
    ``stop``, ``fatal`` or ``end``.

    ``self._results[build_id]['log']`` is a list of tuples such as
    ``(timestamp, step, percent, message)``.
    """
    # pylint: disable = I0011, R0902

    # -------------------------------------------------------------------------
    def __init__(self, settings):
        """Constructor method.

        :param settings: (dictionary)
            Setting dictionary.
        """
        # Attributes
        self.storage_root = settings['storage.root']
        self.build_ttl = int(settings.get('build.ttl', 1800))
        self.result_ttl = int(settings.get('build.result_ttl', 86400))
        self._concurrent = int(settings.get('build.concurrent', 3))
        self._refresh = int(settings.get('agent.refresh', 0))
        self._builds = {}
        self._results = {}

        # Agent list
        self._agents = {}
        total = 0
        for index in range(0, 100):
            pfx = 'agent.%d' % index
            weight = int(settings.get('%s.weight' % pfx, 0))
            if weight:
                self._agents[settings.get('%s.url' % pfx, '')] = [
                    settings.get('%s.password' % pfx, ''), weight, None, 0]
                total += weight
        if total:
            self._concurrent = int(self._concurrent * total
                / float(min([self._agents[k][1] for k in self._agents])))

    # -------------------------------------------------------------------------
    def agent_list(self):
        """Return a list of available agents."""
        return self._agents.keys()

    # -------------------------------------------------------------------------
    def refresh_agent_list(self, request):
        """Refresh processor list for each agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Refresh processor list
        now = time()
        for url in self._agents:
            if self._agents[url][2] is None \
                   or (self._refresh and self._agents[url][3] < now):
                error, processors = self.call(request, url, 'processor_list')
                if error:
                    LOG.error('%s: %s', url, error)
                self._agents[url][2] = processors or []
                self._agents[url][3] = now + self._refresh

        # Refresh processor records
        if self._refresh:
            DBSession.query(Processor).filter(
                Processor.updated + self._refresh < now).delete()
            DBSession.commit()
        processors = [k[0] for k in DBSession.query(Processor.processor_id)]
        for url in sorted(self._agents):
            for processor_id in self._agents[url][2]:
                if processor_id in processors:
                    continue
                error, xml = self.call(
                    request, url, 'processor_xml', processor_id)
                if error:
                    LOG.error('%s: %s', url, error)
                    continue
                processor = Processor.load(processor_id, xml)
                if isinstance(processor, basestring):
                    LOG.error('%s: %s', url,
                              get_localizer(request).translate(processor))
                    continue
                DBSession.add(processor)
                DBSession.commit()

    # -------------------------------------------------------------------------
    def processor(self, request, processor_id):
        """Return a processor tree.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processor_id: (string)
            Processor ID
        :return: (:class:lxml.etree.ElementTree or ``None``)
        """
        self.refresh_agent_list(request)
        xml = DBSession.query(Processor.xml).filter_by(
            processor_id=processor_id).first()
        if xml is not None:
            return etree.parse(StringIO(xml[0].encode('utf8')))

    # -------------------------------------------------------------------------
    def start_build(self, request, processing, processor, pack):
        """Find an agent, convert processing and pack into dictionaries,
        create a build, add it in ``self._builds`` dictionary and try to start
        it.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processing:
            (:class:`~.models.projects.ProjectProcessing` instance)
            Processing object.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param pack: (:class:`~.models.projects.ProjectPack` instance)
            Pack object.
        :return: (:class:`FrontBuild` instance)
        """
        # Compute ID
        self._cleanup()
        build_id = '{prj_id}-{prc_id}-{pck_id}'.format(
            prj_id=processing.project_id, prc_id=processing.processing_id,
            pck_id=pack.pack_id)
        if build_id in self._builds:
            request.session.flash(_('${i}: action already in progress.',
                {'i': build_id}), 'alert')
            return

        # Find agent URL
        agent_url = self._find_url(request, processing.processor)
        if agent_url is None:
            request.session.flash(_('No available agent for ${p}.',
                {'p': processing.processor}), 'alert')
            return

        # Processing dictionary
        processing_dict = {'processor_id': processing.processor,
            'variables': self._variables2dict(request, processing, processor),
            'resources': self._file_set2list(request, processing, 'resource'),
            'templates': self._file_set2list(request, processing, 'template'),
            'output': processing.output}
        if request.session.peek_flash('alert'):
            return

        # Pack dictionary
        pack_dict = {'recursive': pack.recursive,
            'files': self._file_set2list(request, pack, 'file'),
            'resources': self._file_set2list(request, pack, 'resource'),
            'templates': self._file_set2list(request, pack, 'template')}
        if request.session.peek_flash('alert'):
            return

        # Context
        context = {'lang': request.session['lang'],
                   'project_id': request.session['project']['project_id'],
                   'user_id': request.session['user_id']}

        # Create an FrontBuild object
        if build_id in self._results:
            del self._results[build_id]
        self._builds[build_id] = FrontBuild(
            self, build_id, agent_url, context, processing_dict, pack_dict)
        self.start_waiting(request)
        return self._builds[build_id]

    # -------------------------------------------------------------------------
    def build_list(self, project_id):
        """List all builds of a project.

        :param project_id: (integer)
            Project ID.
        :return: (list)
            A list of dictionaries.

        Returned dictionaries are sorted by start time. Each dictionary has
        following keys: ``build_id``, ``start``, ``status``, ``processing_id``,
        ``pack_id``, ``user_id``.
        """
        self._cleanup()
        builds = []
        for build_id, build in self._builds.items():
            if build.result['project_id'] == project_id:
                builds.append({
                    'build_id': build_id, 'start': build.result['log'][0][0],
                    'status': build.result['status'],
                    'processing_id': int(build_id.split('-')[1]),
                    'pack_id': int(build_id.split('-')[2]),
                    'user_id': build.result['user_id']})

        for build_id, result in self._results.items():
            if result['project_id'] == project_id:
                builds.append({
                    'build_id': build_id, 'start': result['log'][0][0],
                    'status': result['status'],
                    'processing_id': int(build_id.split('-')[1]),
                    'pack_id': int(build_id.split('-')[2]),
                    'user_id': result['user_id'],
                    'files': 'files' in result and result['files'] or None})

        return sorted(builds, key=lambda k: k['start'], reverse=True)

    # -------------------------------------------------------------------------
    def is_owner(self, request, build_id, user_id=None):
        """Check if user ``user_id`` has launched the build ``build_id``.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build to check
        :param user_id: (integer, optional)
            User ID to check. By default, the current user is checked.
        :rtype: (boolean)
        """
        if user_id is None:
            user_id = request.session['user_id']
        if (build_id in self._results
                and self._results[build_id]['user_id'] == user_id) \
                or (build_id in self._builds and
                    self._builds[build_id].result['user_id'] == user_id)\
                or has_permission(request, 'prj_manager'):
            return True
        return False

    # -------------------------------------------------------------------------
    def progress(self, request, build_ids):
        """Return the progress of builds.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_ids: (list)
            Build ID list.
        :return: (tuple)
            Return a tuple such as ``(<working>, <progress_dictionary>)``.

        ``<working>`` is a boolean indicating whether one of the processing is
         in progress.

         ``<progress_dictionary>`` is a dictionary such as ``{<build_id>:
         (<step>, <percent>, <message>),...}`` where ``<step>`` is one of the
         following:

        * ``wait``: waiting
        * ``start``: starting
        * ``sync``: synchronizing storages between front and agent
        * ``a_???``: an :class:`~.lib.build.agent.AgentBuildManager` step
        * ``get``: getting result
        * ``warn``: a warning occurred
        * ``error``: an error occurred
        * ``fatal``: a fatal error occurred
        * ``stop``: stopping
        * ``end``: successfully completed
        * ``none``: unknown or not in progress build
        """
        self._cleanup()
        working = False
        prgrss = {}
        for build_id in build_ids:
            if build_id in self._builds:
                prgrss[build_id] = self._builds[build_id].progress(request)
                working = True
            else:
                prgrss[build_id] = ('none', 0, '')
        self.start_waiting(request)
        return working, prgrss

    # -------------------------------------------------------------------------
    def stop(self, request, build_id):
        """Stop a build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build ID.
        """
        self._cleanup()
        if build_id in self._builds:
            self._builds[build_id].stop(request)

    # -------------------------------------------------------------------------
    def complete(self, request, build_id, key):
        """Get the result and eventually download the output directory in
        storage.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build ID.
        :param key: (string)
            Key to authenticate the request.
        :return: (boolean)
        """
        self._cleanup()
        if build_id in self._builds:
            return self._builds[build_id].complete(request, key)
        return build_id in self._results

    # -------------------------------------------------------------------------
    def result(self, request, build_id):
        """Return the result of a build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build ID.
        :return: (tuple)
            A tuple such as ``(<status>, <values>, <files>, <log>)``.

        The status ``<status>`` is one of the following:

        * ``stop``: stopped
        * ``fatal``: in error
        * ``end``: successfuly completed
        """
        self._cleanup()
        if not 'project' in request.session:
            return {}
        project_id = request.session['project']['project_id']
        if build_id in self._results \
               and self._results[build_id]['project_id'] == project_id:
            return self._results[build_id]
        return {}

   # -------------------------------------------------------------------------
    def call(self, request, url, method, *args):
        """Call an agent method directly or via RPC.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param url: (string)
            The agent URL or ``localhost`` to call without RPC.
        :param method: (string)
            Method to call
        :param args:
            Non-keyworded arguments for method.
        :return: (tuple)
            A tuple such as ``(<error>, <result>)`` where ``<error>`` is a
            string and ``<result>`` depends on ``method``.

        In addition to the required arguments, this method sends also a context
        dictionary with ``lang`` (language for error messages), ``front_id``,
        ``password`` (to authenticate front), ``user_id`` and ``local``
        (``True`` if called without XML-RPC). If this method is called for a
        local agent, it adds a ``request`` key in context.
        """
        # Create context
        context = {'lang': request.session['lang'],
                   'front_id': request.registry.settings['uid'],
                   'password': self._agents[url][0],
                   'user_id': request.session['user_id']}

        # Local agent
        if not url:
            context['local'] = True
            context['request'] = request
            try:
                return getattr(xmlrpc, method)(request, context, *args)
            except AttributeError, err:
                return err, None

        # Remote agent
        context['local'] = False
        proxy = xmlrpclib.ServerProxy('%s/xmlrpc' % url, verbose=False)
        try:
            error, result = getattr(proxy, method)(context, *args)
        except IOError, err:
            error, result = err.strerror, None
        except OverflowError, err:
            error, result = err, None
        except xmlrpclib.ProtocolError, err:
            error, result = err.errmsg, None
        except xmlrpclib.Fault, err:
            error, result = err.faultString, None
        return error, result

    # -------------------------------------------------------------------------
    def start_waiting(self, request):
        """Start waiting builds.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Check waiting builds
        waiting = []
        running = 0
        for build_id in self._builds:
            if self._builds[build_id].result['log'][0][1] == 'wait':
                waiting.append(build_id)
            elif not self._builds[build_id].stopped():
                running += 1
        if not waiting or running >= self._concurrent:
            return

        # Start waiting
        waiting = sorted(waiting,
            key=lambda build_id: self._builds[build_id].result['log'][0][0])
        for build_id in waiting[0:self._concurrent - running]:
            self._builds[build_id].start(request)
            sleep(1)
        for build_id in waiting[self._concurrent - running:]:
            self._builds[build_id].expire = time() + self.build_ttl

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete completed builds and expired results and kill long builds."""
        # Build -> result or stop
        now = time()
        for build_id in self._builds.keys():
            if self._builds[build_id].stopped():
                self._results[build_id] = self._builds[build_id].result
                self._results[build_id]['expire'] = now + self.result_ttl
                del self._builds[build_id]
            elif self._builds[build_id].expire < now:
                self._builds[build_id].stop()

        # Remove old results
        for build_id in self._results.keys():
            if self._results[build_id]['expire'] < now:
                del self._results[build_id]

    # -------------------------------------------------------------------------
    def _find_url(self, request, processor_id):
        """Find URL of an agent which serves ``processor_id``.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processor_id: (string)
            ID of the processor agent must serve.
        :return: (string):
            URL of the found agent or ``None``.
        """
        found_url = None
        min_activity = 0
        self.refresh_agent_list(request)
        for url in self._agents:
            if self._agents[url][2] and processor_id in self._agents[url][2]:
                error, activity = self.call(request, url, 'activity')
                if error:
                    LOG.error('%s: %s', url, error)
                    continue
                activity = float(activity + 1) / self._agents[url][1]
                if found_url is None or activity < min_activity:
                    found_url, min_activity = url, activity
        return found_url

    # -------------------------------------------------------------------------
    @classmethod
    def _variables2dict(cls, request, processing, processor):
        """Create a variable dictionary from a processing record and its
        processor.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processing:
            (:class:`~.models.projects.ProjectProcessing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (dictionary)
        """
        values = dict([(k.name, k) for k in processing.variables])
        variables = {}
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            value = values[name].value if name in values \
                    else var.findtext('default') is not None \
                    and var.findtext('default').strip() or ''
            if var.get('type') == 'string':
                variables[name] = value
            elif var.get('type') == 'boolean':
                variables[name] = bool(value == 'true' or value == '1')
            elif var.get('type') == 'integer':
                variables[name] = int(value)
            elif var.get('type') == 'select':
                if not value in [k.get('value') or k.text
                                 for k in var.findall('option')]:
                    request.session.flash(
                        _('${v}: bad value.', {'v': name}), 'alert')
                    return variables
                variables[name] = int(value) if value.isdigit() else value
            elif var.get('type') == 'regex':
                if not re.match(var.find('pattern').text, value):
                    request.session.flash(
                        _('${v}: bad value.', {'v': name}), 'alert')
                    return variables
                variables[name] = int(value) if value.isdigit() else value
        return variables

    # -------------------------------------------------------------------------
    @classmethod
    def _file_set2list(cls, request, record, file_type):
        """Save set of files in a list.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param record: (:class:`~.models.projects.ProjectProcessing`
            or :class:`~.models.projects.ProjectPack` instance).
        :param file_type: ('file', 'resource' or 'template')
            File type.
        """
        file_set = []
        items = [k for k in record.files if k.file_type == file_type]
        if len(items) == 0:
            return file_set

        storage_root = request.registry.settings['storage.root']
        for item in items:
            if not exists(join(storage_root, item.path)):
                request.session.flash(
                    _('"${n}" does not exists.', {'n': item.path}), 'alert')
                return
            if file_type in ('file', 'resource'):
                file_set.append(item.path)
            else:
                file_set.append((item.path, item.target))

        return file_set


# =============================================================================
class FrontBuild(object):
    """This class manages a build locally and via an agent.

    ``self.result`` is a dictionary with following keys: ``status``, ``log``,
    ``start``, ``expire``, ``project_id``, ``user_id``. At the process end, it
    can also have ``files``, ``values``, ``error`` and ``end`` keys.

    ``self.result['log']`` is a list of tuples such as ``(timestamp, step,
    percent, message)``.

    ``self.result['expire']`` is the date beyond which the build is destroyed.

    ``self.key`` is a key to authenticate transaction between front and
    agent.
    """
    # pylint: disable = I0011, R0902, R0913

    # -------------------------------------------------------------------------
    def __init__(self, build_manager, build_id, agent_url, context,
                 processing, pack):
        """Constructor method.

        :param build_manager: (:class:`FrontBuildManager` instance)
            Application :class:`FrontBuildManager` object.
        :param build_id: (string)
            Build ID.
        :param agent_url: (string)
            URL to call to complete process.
        :param context: (dictionary)
            A dictionary with with ``project_id``, ``lang`` and ``user_id``
            keys.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
         """
        self.uid = build_id
        self._build_manager = build_manager
        self._agent_url = agent_url
        self._processing = processing
        self._pack = pack
        self._lang = context['lang']
        self._thread = None
        self.key = str(randint(1000, 9999999))
        self.expire = time() + build_manager.build_ttl
        self.result = {'status': 'none',
            'log': [(time(), 'wait', 1, self._translate(_('waiting...')))],
            'project_id': context['project_id'], 'user_id': context['user_id']}

    # -------------------------------------------------------------------------
    def start(self, request):
        """Start a build in a thread.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        if self._thread is None:
            self._thread = Thread(
                target=self._thread_start, kwargs={'request': request})
            self.result['log'] = [
                (time(), 'start', 1, self._translate(_('startup')))]
            self._thread.start()

    # -------------------------------------------------------------------------
    def progress(self, request):
        """Return the progress of build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (tuple)
            A tuple such as ``(<step>, <percent>, <message>, <start_time>)``.
        """
        if self.result['log'][-1][1][0:2] != 'a_':
            return self.result['log'][-1][1:] + (self.result['log'][0][0],)

        error, prgrss = self._build_manager.call(
            request, self._agent_url, 'progress', self.uid)
        if error:
            self.stopped(error, 'a_error')
            return self.result['log'][-1][1:] + (self.result['log'][0][0],)
        if prgrss[0] == 'none':
            self.stopped(_('agent build destroyed'))
            prgrss = self.result['log'][-1][1:]
        elif prgrss[0] in ('a_end', 'a_stop', 'a_fatal'):
            self.complete(request, self.key)
            prgrss = self.result['log'][-1][1:]
        return tuple(prgrss) + (self.result['log'][0][0],)

    # -------------------------------------------------------------------------
    def stop(self, request=None):
        """Stop building."""
        if request is not None and self.result['log'][-1][1][0:2] == 'a_':
            error = self._build_manager.call(
                request, self._agent_url, 'stop', self.uid)[0]
            if error:
                self.stopped(error)
        elif not self.stopped():
            self._log(_('stopped'), 'stop', 100)
            self.result['message'] = _('Stopped by user')
            self.result['status'] = 'stop'

    # -------------------------------------------------------------------------
    def stopped(self, error=None, level='fatal'):
        """Check if there is a fatal error and if the build is stopped.

        :param error: (string, optional)
            Error message.
        :param level: (string, default='fatal')
            Error level: ``warn``, ``error`` or ``fatal``.
        :return: (boolean)
            ``True`` if it is stopped.
        """
        if error:
            if level == 'fatal':
                self.result['status'] = level
                self.result['message'] = error
            self._log(error, level, 100)

        return self.result['status'] in ('stop', 'fatal', 'end')

    # -------------------------------------------------------------------------
    def complete(self, request, key):
        """Start a *complete* action in a thread.

        :param request: (object)
            WebOb request object.
        :param key: (string)
            Authentication key.
        :return: (boolean)
            ``True`` if succeeds.
        """
        if self.result['log'][-1][1][0:2] != 'a_' or self.key != key or \
               (self._thread is not None and self._thread.is_alive()):
            return False
        self._log(_('getting log and result'), 'get')

        # Update request
        user = DBSession.query(User)\
               .filter_by(user_id=int(self.result['user_id'])).first()
        if user is None:
            self.stopped(_('unknown user'))
            return False
        user.setup_environment(request)
        DBSession.close()

        # Launch thread
        if self._thread is not None:
            del self._thread
        self._thread = Thread(
            target=self._thread_complete, kwargs={'request': request})
        self._thread.start()
        return True

    # -------------------------------------------------------------------------
    def _log(self, message, step=None, percent=None):
        """Append an entry to ``result['log']``.

        :param message: (string)
            Message to write to the log.
        :param step: (string, optional)
            If not ``None``, progress is updated.
        :param percent: (int, optional)
            Percent of progress for step ``<step>``.

        ``self.result['log']`` is a list of tuples such as ``(<timestamp>,
        <step>, <percent>, <message>)``.
        """
        if percent is None:
            percent = self.result['log'][-1][2] if step is None else 0

        if step is None:
            step = self.result['log'][-1][1]

        self.result['log'].append(
            (time(), step, percent, self._translate(message)))

    # -------------------------------------------------------------------------
    def _thread_start(self, request):
        """Action launched in a thread to start a build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Synchronize storages with buildspaces
        if self._agent_url:
            self._storage2buildspace(request)
        if self.stopped():
            return

        # Start build
        end_url = request.route_url(
            'build_complete', build_id=self.uid, key=self.key)
        self.expire = time() + self._build_manager.build_ttl
        if self._agent_url:
            self._log(_('call ${url}', {'url': self._agent_url}), 'a_call')
        else:
            self._log(_('call agent'), 'a_call')
        error = self._build_manager.call(request, self._agent_url, 'start',
            self.uid, self._processing, self._pack, end_url)[0]
        self.stopped(error)

    # -------------------------------------------------------------------------
    def _thread_complete(self, request):
        """Action launched in a thread to get the result and, eventually,
        download the output directory in storage.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Get result
        error, result = self._build_manager.call(
            request, self._agent_url, 'result', self.uid)
        if self.stopped(error):
            self._build_manager.start_waiting(request)
            return
        self.result['log'][-1:1] += result['log']
        if result['status'] == 'none':
            self.stopped(_('agent build destroyed'))
            self._build_manager.start_waiting(request)
            return
        elif result['status'] != 'a_end':
            self.result['status'] = result['status'][2:]
            self.result['message'] = result['message']
            self._build_manager.start_waiting(request)
            return

        # Transfer result
        if 'values' in result:
            self.result['values'] = result['values']
        if 'files' in result:
            self.result['files'] = result['files']

        # Download output directory in storage
        if self.result.get('files') and self._processing['output']:
            self._output2storage(request)
            if self.stopped():
                del self.result['files']
                self._build_manager.start_waiting(request)
                return

        # End
        if [True for k in self.result['log'] if k[1] in ('error', 'a_error')]:
            self.stopped(_('error occurred'))
            self._build_manager.start_waiting(request)
            return
        self._log(_('successfully completed'), 'end', 100)
        self.result['message'] = _('Successfully completed')
        self.result['status'] = 'end'
        self._build_manager.start_waiting(request)

    # -------------------------------------------------------------------------
    def _storage2buildspace(self, request):
        """Synchronize storages on front with buildspaces on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Make list of files to synchronize
        file_list = list(self._processing['resources']) \
                    + [k[0] for k in self._processing['templates']] \
                    + list(self._pack['files']) \
                    + list(self._pack['resources']) \
                    + [k[0] for k in self._pack['templates']]
        total = len(file_list)

        # Browse names and synchronize
        for index, name in enumerate(file_list):
            self._log(_('synchronizing ${n}', {'n': name}),
                      'sync', 100 * index / total)
            fullname = join(request.registry.settings['storage.root'], name)
            if not exists(fullname):
                continue
            if isfile(fullname):
                self._file2buildspace(request, name)
            else:
                self._dir2buildspace(request, name)
            if self.stopped():
                return

        self._log(_('synchronization completed'), 'sync', 100)
        return True

    # -------------------------------------------------------------------------
    def _dir2buildspace(self, request, directory):
        """Synchronize a directory in storage on front with its copy in
        buildspace on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param directory: (string)
            Relative path to storage directory of directory to synchronize.
        """
        # Get directory content
        fullpath = join(request.registry.settings['storage.root'],
                        directory)
        file_list = []
        for path, dirs, files in walk(fullpath):
            for name in set(dirs) & set(EXCLUDED_FILES):
                dirs.remove(name)
            for name in files:
                file_list.append(relpath(join(path, name), fullpath))

        # In destination, remove deleted files
        error = self._build_manager.call(request, self._agent_url,
            'buildspace_cleanup', directory, file_list)[0]
        if self.stopped(error):
            return

        # Synchronize files
        for name in file_list:
            self._file2buildspace(request, join(directory, name))
            if self.stopped():
                return

    # -------------------------------------------------------------------------
    def _file2buildspace(self, request, filename):
        """Synchronize a file in storage on front with its copy in buildspace
        on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param filename: (string)
            Relative path to storage directory of file to synchronize.
        """
        # Get file signature
        error, sig = self._build_manager.call(
            request, self._agent_url, 'buildspace_send_signature', filename)
        if self.stopped(error):
            return
        stg_path = request.registry.settings['storage.root']

        # Transfer full file
        if not sig:
            with open(join(stg_path, filename), 'rb') as hdl:
                error = self._build_manager.call(
                    request, self._agent_url, 'buildspace_receive_file',
                    filename, xmlrpclib.Binary(hdl.read()))[0]
            self.stopped(error)
            return

        # Transfer delta
        with open(join(stg_path, filename), 'rb') as hdl:
            delta_file = DeltaFile(sig.data, hdl)
            delta_buf = delta_file.read()
            delta_file.close()
        if not delta_buf or self.stopped():
            return
        error = self._build_manager.call(
            request, self._agent_url, 'buildspace_receive_delta', filename,
            xmlrpclib.Binary(delta_buf))[0]
        self.stopped(error)

    # -------------------------------------------------------------------------
    def _output2storage(self, request):
        """Copy output on agent in storage on front.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Authorized?
        storage, root, user = self._storage4output(request)
        if storage is None:
            DBSession.close()
            return

        # Local agent
        if not self._agent_url:
            output_dir = join(request.registry.settings['build.root'],
                camel_case(self.uid), 'Output')
            if not exists(output_dir):
                self.stopped(_('Output directory has been destroyed.'))
                DBSession.close()
                return
            copy_content(output_dir, root)
        # Remote agent
        else:
            error, files = self._build_manager.call(
                request, self._agent_url, 'output_list', self.uid)
            if self.stopped(error) or not len(files):
                DBSession.close()
                return
            total = len(files)
            for index, filename in enumerate(files):
                self._log(_('getting ${f}', {'f': filename}),
                          'get', 100 * index / total)
                self._file2storage(request, root, filename)
                if self.stopped():
                    DBSession.close()
                    return

        # Add in VCS
        handler = request.registry['handler']\
              .get_handler(storage.storage_id, storage)
        if storage.vcs_engine != 'none':
            message = get_localizer(request).translate(
                _('Produced by processing'))
            handler.add((user and user.vcs_user or None,
                     user and decrypt(user.vcs_password,
                        request.registry.settings['auth.key']),
                     request.session['name']),
                    self._processing['output'].partition('/')[2], message)
            error, message = handler.progress()
            if error == 'error':
                self.stopped(message)
        handler.cache.clear()

        DBSession.close()
        if not self.stopped():
            self._log(_('result received'), 'get', 100)

    # -------------------------------------------------------------------------
    def _file2storage(self, request, root, filename):
        """Synchronize a file in build directory on agent with one in storage
        on front.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param root: (string)
            Absolute root path for file to synchronize.
        :param filename: (string)
            Name of the file to synchronize.
        """
        fullname = normpath(join(root, filename))
        if not fullname.startswith(root):
            self.stopped(_('Access was denied to this resource.'))
            return
        if not exists(dirname(fullname)):
            makedirs(dirname(fullname))

        # Transfer full file
        if not exists(fullname):
            error, content = self._build_manager.call(request, self._agent_url,
                'output_send_file', self.uid, filename)
            if self.stopped(error):
                return
            with open(fullname, 'wb') as hdl:
                hdl.write(content.data)
            return

        # Transfer delta
        sig_file = SigFile(open(fullname, 'rb'), get_block_size(fullname))
        sig_buf = sig_file.read()
        sig_file.close()
        error, delta = self._build_manager.call(request, self._agent_url,
            'output_send_delta', self.uid, filename, xmlrpclib.Binary(sig_buf))
        if self.stopped(error):
            return

        # Patch
        patch_file = PatchedFile(open(fullname, 'rb'), StringIO(delta.data))
        temp_name = '%s~%d~' % (fullname, randint(1, 999999))
        with open(temp_name, 'wb') as hdl:
            hdl.write(patch_file.read())
        patch_file.close()
        if exists(temp_name):
            rename(temp_name, fullname)

   # -------------------------------------------------------------------------
    def _storage4output(self, request):
        """Get the corresponding storage of an output if exists and if user
        is authorized.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (tuple)
            A tuple such as ``(storage, root, user)`` where ``storage`` is
            a :class:`~.models.storages.Storage` object, ``root`` the
            absolute root path for files to transfer and ``user`` a
            :class:`~.models.storage.StorageUser` object.
        """
        # Storage
        storage_id = self._processing['output'].partition('/')[0]
        storage = DBSession.query(Storage).filter_by(
            storage_id=storage_id).first()
        if storage is None:
            self.stopped(_('This storage does not exist!'))
            return None, None, None

        # Root path
        storage_root = normpath(request.registry.settings['storage.root'])
        root = normpath(join(storage_root, self._processing['output']))
        if not root.startswith(storage_root):
            self.stopped(_('Access was denied to this resource.'))
            return None, None, None

        # User
        user = DBSession.query(StorageUser).filter_by(
            storage_id=storage_id,
            user_id=request.session['user_id']).first()
        if not has_permission(request, 'stg_modifier') \
                and storage.access != 'open' \
                and (not user or not user.perm or user.perm == 'user'):
            self.stopped(_('You do not have access to this storage!'))
            return None, None, None

        if storage.vcs_engine not in ('none', 'local') \
               and not (user and user.vcs_user):
            self.stopped(_('ID and password for storage are missing.'))
            return None, None, None

        return storage, root, user

    # -------------------------------------------------------------------------
    def _translate(self, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to trnaslate.
        """
        return localizer(self._lang or 'en').translate(text)
