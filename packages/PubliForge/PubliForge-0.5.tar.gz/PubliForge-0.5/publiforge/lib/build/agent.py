# $Id: agent.py 87b7d52fda37 2012/02/23 17:08:44 patrick $
"""Agent build management.

An *agent* is a Web service.
"""

import logging
from os import listdir, makedirs
from os.path import exists, join, getatime, normpath, dirname
from lxml import etree
from threading import Thread
from time import time
from fnmatch import fnmatch
import shutil
import urllib

from pyramid.asset import abspath_from_asset_spec

from ..utils import _, localizer, copy_content, camel_case
from ..xml import load


LOG = logging.getLogger(__name__)


# =============================================================================
class AgentBuildManager(object):
    """This class manages agent builds.

    One instance of :class:`AgentBuildManager` is created during application
    initialization. It is only used in agent mode. It is stored in application
    registry.

    ``self._processors`` is a tuple such as ``(processor_dictionary, path_list,
    available_list)``. ``processor_dictionary`` is a dictionary such as
    ``{processor_id: processor_path,...}``.

    ``self._fronts`` is a dictionary such as ``{front_id: password,...}``.

    ``self._builds`` is a dictionary of :class:`AgentBuild` objects.

    ``self._results`` is a dictionary of dictionaries such as ``{build_id:
    result_dict}``. ``result_dict`` is a dictionary with following keys:
    ``status``, ``log``, ``expire``. According to build events, it can also
    contains ``files``, ``values`` and ``error`` keys.

    ``self._results[build_id]['status']`` is one of the following strings:
    ``a_stop``, ``a_fatal`` or ``a_end``.

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
        self.develop = bool(settings.get('build.develop') == 'true')
        self.buildspace_root = settings.get('buildspace.root')
        self.storage_root = settings.get('storage.root')
        self.build_root = settings['build.root']
        self.build_ttl = int(settings.get('build.ttl', 1800))
        self.result_ttl = int(settings.get('build.result_ttl', 86400))
        self._concurrent = int(settings.get('build.concurrent', 3))
        self._buildspace_ttl = int(settings.get('buildspace.ttl', 2678400))
        self._builds = {}
        self._results = {}

        # Processor list
        self._processors = [
            {}, tuple(settings.get('processor.roots', '').split()),
            tuple(settings.get('processor.available', '').split())]

        # Authorized front list
        self._fronts = {}
        for idx in range(100):
            if 'front.%d.uid' % idx in settings:
                self._fronts[settings['front.%d.uid' % idx]] = \
                       settings.get('front.%d.password' % idx, '')

    # -------------------------------------------------------------------------
    def processor_list(self):
        """Refresh information and return a list of available processors."""
        self._processors[0] = {}
        self.add_processors(join(dirname(__file__), '..', '..', 'Processors'))
        for path in self._processors[1]:
            self.add_processors(path)
        plist = []
        for pid in self._processors[0]:
            for pattern in self._processors[2]:
                if pid not in plist and fnmatch(pid, pattern):
                    plist.append(pid)
                    break
        return plist

    # -------------------------------------------------------------------------
    def add_processors(self, path):
        """Add all processors in path ``path``.

        :param path: (string)
             Where to look for processors.
        """
        path = abspath_from_asset_spec(path)
        if not exists(path):
            return

        for pid in listdir(path):
            if exists(join(path, pid, 'processor.xml')):
                self._processors[0][pid] = normpath(join(path, pid))

    # -------------------------------------------------------------------------
    def processor_path(self, processor_id):
        """Return processor path if exists.

        :param processor_id: (string)
            Processor ID.
        :return: (string)
        """
        return self._processors[0].get(processor_id)

    # -------------------------------------------------------------------------
    def processor_xml(self, processor_id):
        """Return processor XML if exists.

        :param processor_id: (string)
            Processor ID.
        :return: (string)
        """
        if not processor_id in self._processors[0]:
            return ''
        tree = load(
            join(self._processors[0][processor_id], 'processor.xml'),
            {'publiforge': join(dirname(__file__), '..', '..', 'RelaxNG',
             'publiforge.rng')})
        if isinstance(tree, basestring):
            return ''
        etree.strip_elements(tree, etree.Comment)
        return ' '.join(etree.tostring(tree, encoding='utf8').split())

    # -------------------------------------------------------------------------
    def front_list(self):
        """Return a list of authorized fronts."""
        return self._fronts.keys()

    # -------------------------------------------------------------------------
    def authorized_front(self, front_id, password):
        """``True`` if ``front_id`` is authorized to use agent services."""
        return front_id in self._fronts and self._fronts[front_id] == password

    # -------------------------------------------------------------------------
    def activity(self):
        """Return the global activity i.e. the number of active builds."""
        return len(self._builds)

    # -------------------------------------------------------------------------
    def start_build(self, build_id, context, processing, pack, end_url=None):
        """Create a build, add it in ``self._builds`` dictionary and try to
        start it.

        :param build_id: (string)
            Build ID.
        :param context: (dictionary)
            See :class:`~.front.FrontBuildManager`
            :meth:`~.front.FrontBuildManager.call` method.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
        :param end_url: (string, optional)
            URL to call to complete the build.
        :return: (:class:`~AgentBuild`)
        """
        self._cleanup()
        self._cleanup_directories()
        if build_id in self._builds:
            build = self._builds[build_id]
        else:
            if build_id in self._results:
                del self._results[build_id]
            build = self._builds[build_id] = AgentBuild(
                self, build_id, context, processing, pack, end_url)
        self.start_waiting()
        return build

    # -------------------------------------------------------------------------
    def progress(self, build_id):
        """Return the progress of build.

        :param build_id: (string)
            Build ID.
        :return: (tuple)
            A tuple such as ``(<step>, <percent>, <message>)``.

        The step ``<step>`` is one of the following:

        * ``a_start``: starting
        * ``a_env``: importing processor environment
        * ``a_build``: building
        * ``a_warn``: a warning occurred
        * ``a_error``: an error occurred
        * ``a_fatal``: a fatal error occurred
        * ``a_stop``: stopping
        * ``a_end``: successfully completed
        * ``none``: unknown or not in progress build
        """
        self._cleanup()
        if build_id in self._builds and self._builds[build_id].result['log']:
            return self._builds[build_id].result['log'][-1][1:]
        elif build_id in self._results:
            return self._results[build_id]['log'][-1][1:]
        self.start_waiting()
        return 'none', 0, ''

    # -------------------------------------------------------------------------
    def stop(self, build_id):
        """Stop a build.

        :param build_id: (string)
            Build ID.
        """
        self._cleanup()
        if build_id in self._builds:
            self._builds[build_id].stop()
        return ''

    # -------------------------------------------------------------------------
    def result(self, build_id):
        """Return the result of build.

        :param build_id: (string)
            Build ID.
        :return: (dictionary)
            ``self._result`` or ``{'status': 'none'}``.

        The status ``<status>`` is one of the following:

        * ``a_stop``: stopped
        * ``a_fatal``: a fatal error occurred
        * ``a_end``: successfuly completed
        * ``none``: unknown build
        """
        self._cleanup()
        self._cleanup_directories()
        return self._results[build_id] if build_id in self._results \
               else {'status': 'none', 'log': [], 'message': ''}

    # -------------------------------------------------------------------------
    def start_waiting(self):
        """Start waiting builds."""
        # Check waiting builds
        running = 0
        waiting = []
        for build_id in self._builds:
            if self._builds[build_id].result['log'][0][1] == 'a_wait':
                waiting.append(build_id)
            elif not self._builds[build_id].stopped():
                running += 1
        if running >= self._concurrent or not waiting:
            return

        # Start waiting
        waiting = sorted(waiting,
            key=lambda build_id: self._builds[build_id].result['log'][0][0])
        for build_id in waiting[self._concurrent - running:]:
            self._builds[build_id].expire = time() + self.build_ttl
        for build_id in waiting[0:self._concurrent - running]:
            self._builds[build_id].start()

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete completed builds and expired results and kill long builds."""
        # Build -> result or stop
        now = time()
        for build_id in self._builds.keys():
            if self._builds[build_id].stopped():
                self._builds[build_id].result['expire'] = now + self.result_ttl
                self._results[build_id] = self._builds[build_id].result
                del self._builds[build_id]
            elif self._builds[build_id].expire < now:
                self._builds[build_id].stop()

        # Remove old results
        for build_id in self._results.keys():
            if now > self._results[build_id]['expire']:
                del self._results[build_id]

    # -------------------------------------------------------------------------
    def _cleanup_directories(self):
        """Remove old directories."""
        # Clean up buid path
        now = time()
        if exists(self.build_root):
            for name in listdir(self.build_root):
                path = join(self.build_root, name)
                if not name in self._builds and exists(path) \
                       and getatime(path) + self.result_ttl < now:
                    shutil.rmtree(path)

        # Clean up buidspace path
        if self.buildspace_root is not None and exists(self.buildspace_root):
            for name in listdir(self.buildspace_root):
                path = join(self.buildspace_root, name)
                if exists(path) \
                       and getatime(path) + self._buildspace_ttl < now:
                    shutil.rmtree(path)


# =============================================================================
class AgentBuild(object):
    """This class manages one local build.

    ``self.result`` is a dictionary with the following keys: ``status``,
    ``message``, ``log``. Log entry is a list of tuples such as ``(<timestamp>,
    <step>, <percent>, <message>)``. Engine can add keys like: ``files``,
    ``values``.
    """
    # pylint: disable = I0011, R0902, R0913

    # -------------------------------------------------------------------------
    def __init__(self, build_manager, build_id, context, processing, pack,
                 end_url):
        """Constructor method.

        :param build_manager: (:class:`AgentBuildManager` instance)
            Application :class:`AgentBuildManager` object.
        :param build_id: (string)
            Build ID.
        :param context: (dictionary)
            See :class:`~publiforge.lib.build.front.FrontBuildManager`
            :meth:`~publiforge.lib.build.front.FrontBuildManager.call`
            method.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
        :param end_url: (string, optional)
            URL to call to complete the build.
        """
        self.build_id = build_id
        self.context = context
        self.path = join(build_manager.build_root, camel_case(build_id))
        self.data_path = context['local'] and build_manager.storage_root \
                         or build_manager.buildspace_root
        self.result = {'status': 'none',
            'log': [(time(), 'a_wait', 1, self._translate(_('waiting...')))],
            'message': ''}
        self.expire = time() + build_manager.build_ttl
        self.processing = processing
        self.pack = pack
        self._build_manager = build_manager
        self._end_url = end_url
        self._thread = None
        if not exists(self.path):
            makedirs(self.path)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processing."""
        # Already started
        if self._thread is not None:
            self.stopped(_('Already in progress'), 'a_warn')
            return
        self.result['log'] = [(
            time(), 'a_start', 1, self._translate(_('agent build startup')))]

        # Create build directory
        proc_path = join(self.path, 'Processor')
        if self._build_manager.develop and exists(proc_path):
            shutil.rmtree(proc_path)
        if not exists(proc_path):
            makedirs(proc_path)
            if not self._import_processor(self.processing['processor_id']):
                self.stopped(self.result['message'])
                return
            if not exists(join(self.path, 'Output')):
                makedirs(join(self.path, 'Output'))
            self.log(_('processor environment installed'), 'a_env', 100)

        # Build directly...
        if self._end_url is None:
            self._thread_engine()

        # ...or in a thread
        self._thread = Thread(target=self._thread_engine)
        self._thread.start()

    # -------------------------------------------------------------------------
    def stop(self):
        """Stop building."""
        if not self.stopped():
            self.result['status'] = 'a_stop'
            self.result['message'] = self._translate(_('Stop by user'))
            self.log(_('stopped'), 'a_stop', 100)

    # -------------------------------------------------------------------------
    def stopped(self, error=None, level='a_fatal'):
        """Check if there is a fatal error and if the build is stopped.

        :param error: (string, optional)
            Error message.
        :param level: (string, default='a_fatal')
            Error level: ``a_warn``, ``a_error`` or ``a_fatal``.
        :return: (boolean)
            ``True`` if it is stopped.
        """
        if error:
            if level == 'a_fatal':
                self.result['status'] = level
                self.result['message'] = self._translate(error)
            self.log(error, level, 100)

        return self.result['status'] in ('a_stop', 'a_fatal', 'a_end')

    # -------------------------------------------------------------------------
    def log(self, message, step=None, percent=None):
        """Append an entry to ``result['log']``.

        :param message: (string)
            Message to write in log.
        :param step: (string, optional)
            If not ``None``, progress is updated.
        :param percent: (int, optional)
            Percent of progress for step ``<step>``.
        """
        if percent is None:
            percent = self.result['log'][-1][2] if step is None else 0
        if step is None:
            step = self.result['log'][-1][1]

        self.result['log'].append(
            (time(), step, percent, self._translate(message)))

        if self.context['local'] and not 'request' in self.context:
            {'a_warn': LOG.warning, 'a_error': LOG.error,
             'a_fatal': LOG.critical
             }.get(step,  LOG.info)(self.result['log'][-1][3])

    # -------------------------------------------------------------------------
    def _thread_engine(self):
        """Action in a thread to launch engine."""
        # Find the engine
        tree = etree.parse(join(self.path, 'Processor', 'processor.xml'))
        module_name = tree.findtext('processor/engine').strip()
        try:
            module = __import__(module_name, fromlist=['Engine'])
        except ImportError, err:
            self.stopped('%s: %s' % (module_name, err))

        # Launch engine
        if not self.stopped():
            self.log(_('start engine'), 'a_build')
            self.expire = time() + self._build_manager.build_ttl
            module.Engine(self).start()
            if not self.stopped():
                self.log(_('agent build completed'), 'a_end', 100)
                self.result['status'] = 'a_end'

        # Announce the end to the front
        if self._end_url is None:
            self._build_manager.start_waiting()
            return
        if not self.context['local']:
            try:
                response = urllib.urlopen(self._end_url)
            except IOError, err:
                self._build_manager.start_waiting()
                return
            response.close()
        elif 'request' in self.context:
            request = self.context['request']
            request.registry['fbuild'].complete(
                request, self.build_id, self._end_url.split('/')[-1])
        self._build_manager.start_waiting()

    # -------------------------------------------------------------------------
    def _import_processor(self, processor_id):
        """Import processor, eventually with inheritance, in build directory.

        :param processor_id: (string)
            ID of processor to import.
        :return: (boolean)
            ``True`` if it succeeds.
        """
        # Find processor
        src_path = self._build_manager.processor_path(processor_id)
        if not src_path:
            self.stopped(_('Unknown processor "${p}"', {'p': processor_id}))
            return False

        # Read processor.xml file to check if other processor is needed
        ancestors = etree.parse(join(src_path, 'processor.xml'))\
                   .findall('processor/ancestors/ancestor')
        for ancestor in ancestors:
            if not self._import_processor(ancestor.text.strip()):
                return False

        # Copy processor
        copy_content(src_path, join(self.path, 'Processor'))
        return True

    # -------------------------------------------------------------------------
    def _translate(self, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(self.context['lang']).translate(text)
