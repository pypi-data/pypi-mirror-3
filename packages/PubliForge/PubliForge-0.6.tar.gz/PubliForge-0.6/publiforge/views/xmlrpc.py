# $Id: xmlrpc.py b1ffa5a75b89 2012/02/19 23:23:01 patrick $
"""These XML-RPC functions are called by the front method
:meth:`~.lib.build.front.FrontBuildManager.call`"""

from os import listdir, remove, walk, makedirs, rename
from os.path import exists, join, dirname, relpath, normpath
from shutil import rmtree
from cStringIO import StringIO
from random import randint
import xmlrpclib

from ..lib.utils import _, localizer, camel_case
from ..lib.rsync import get_block_size
from ..lib.rsync import SigFile, PatchedFile, DeltaFile


# =============================================================================
def processor_list(request, context):
    """Return a list of available processors.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :return: (tuple)
        ``(error, processor_list)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)
    return '', request.registry['abuild'].processor_list()


# =============================================================================
def processor_xml(request, context, processor_id):
    """Return XML of processor ``processor_id``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param processor_id: (string)
        Processor_id
    :return: (tuple)
        ``(<error>, <processor_list>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)
    return '', request.registry['abuild'].processor_xml(processor_id)


# =============================================================================
def activity(request, context):
    """Return the agent activity i.e. the number of active builds.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param password: (string)
        Front password to use agent services.
    :return: (tuple)
        ``(<error>, <activity>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)
    return '', request.registry['abuild'].activity()


# =============================================================================
def start(request, context, build_id, processing, pack, end_url):
    """Start the build.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :param processing: (dictionary)
        A processing dictionary.
    :param pack: (dictionary)
        A pack dictionary.
    :param end_url: (string)
        URL to call to complete the build.
    :return: (tuple)
        ``(<error>, '')``

    Arguments of this RPC function are: ``<front_id>, <password>, <user>,
    <build_id>, <processing>, <pack>, <end_url>``.
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Adjust paths
    if not context['local']:
        processing['resources'] = _agent_paths(
            request, context, *processing['resources'])
        for item in processing['templates']:
            item[0] = _agent_paths(request, context, item[0])[0]
        pack['files'] = _agent_paths(request, context, *pack['files'])
        pack['resources'] = _agent_paths(request, context, *pack['resources'])
        for item in pack['templates']:
            item[0] = _agent_paths(request, context, item[0])[0]

    # Start build
    build_id = _agent_build_id(request, context, build_id)
    request.registry['abuild'].start_build(
        build_id, context, processing, pack, end_url)
    return '', ''


# =============================================================================
def progress(request, context, build_id):
    """Return the progress of a build.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :return: (tuple)
        ``(<error>, <result>)``
    """
    return _agent_method(request, context, build_id, 'progress')


# =============================================================================
def stop(request, context, build_id):
    """Stop a build.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :return: (tuple)
        ``(<error>, <result>)``
    """
    return _agent_method(request, context, build_id, 'stop')


# =============================================================================
def result(request, context, build_id):
    """Return the result of a build.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    """
    return _agent_method(request, context, build_id, 'result')


# =============================================================================
def buildspace_cleanup(request, context, path, filenames):
    """Delete files in path ``path`` of buildspace directory which are not in
    ``files``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param path: (string)
        Path to clean up.
    :param filenames: (list)
        Names of file to keep.
    :return: (tuple)
        ``(<error>, '')``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Clean directory
    root = join(request.registry.settings['buildspace.root'],
                _agent_paths(request, context, path)[0])
    if not exists(root):
        return '', ''
    for path, dirs, files in walk(root, topdown=False):
        for name in files:
            if not normpath(join(relpath(path, root), name).decode('utf8')) \
                   in filenames and exists(join(path, name)):
                remove(join(path, name))
        for name in dirs:
            if not listdir(join(path, name)):
                rmtree(join(path, name))
    return '', ''


# =============================================================================
def buildspace_send_signature(request, context, filename):
    """Return signature of a buildspace file.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param filename: (string)
        Filename that should send the signature.
    :return: (tuple)
        ``(<error>, <signature>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Empty string or signature
    filename = join(request.registry.settings['buildspace.root'],
                    _agent_paths(request, context, filename)[0])
    if not exists(filename):
        return '', ''
    sig_file = SigFile(open(filename, 'rb'), get_block_size(filename))
    sig_buf = sig_file.read()
    sig_file.close()
    return '', xmlrpclib.Binary(sig_buf)


# =============================================================================
def buildspace_receive_file(request, context, filename, content):
    """Receive a file in buildspace directory.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param filename: (string)
        Filename that should send the signature.
    :param content: (:class:`xmlrpclib.Binary` instance)
        File content.
    :return: (tuple)
        ``(<error>, '')``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Write file
    filename = join(request.registry.settings['buildspace.root'],
                    _agent_paths(request, context, filename)[0])
    if exists(filename):
        return '', ''
    path = dirname(filename)
    if not exists(path):
        makedirs(path)
    with open(filename, 'wb') as hdl:
        hdl.write(content.data)
    return '', ''


# =============================================================================
def buildspace_receive_delta(request, context, filename, delta):
    """Receive a delta (rsync) for a file in buildspace directory.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param filename: (string)
        Filename that should send the signature.
    :param delta: (:class:`xmlrpclib.Binary` instance)
        Patch to apply.
    :return: (tuple)
        ``(<error>, '')``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Patch file
    filename = join(request.registry.settings['buildspace.root'],
                    _agent_paths(request, context, filename)[0])
    if not exists(filename):
        return _error(context, _('Unknown file "${n}"', {'n': filename}))

    patch_file = PatchedFile(open(filename, 'rb'), StringIO(delta.data))
    temp_name = '%s~%d~' % (filename, randint(1, 999999))
    with open(temp_name, 'wb') as hdl:
        hdl.write(patch_file.read())
    patch_file.close()
    if exists(temp_name):
        rename(temp_name, filename)
    return '', ''


# =============================================================================
def output_list(request, context, build_id):
    """List output files of a build.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :return: (tuple)
        ``(<error>, <file_list>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # List files
    build_id = _agent_build_id(request, context, build_id)
    output = join(request.registry.settings['build.root'],
                  camel_case(build_id), 'Output')
    file_list = []
    for path, name, files in walk(output):
        for name in files:
            file_list.append(relpath(join(path, name), output))
    return '', file_list


# =============================================================================
def output_send_file(request, context, build_id, filename):
    """Send a file of the ``Output`` directory.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :param filename: (string)
        Name of the file to transfer.
    :return: (tuple)
        ``(<error>, <file_content>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Send file
    build_id = _agent_build_id(request, context, build_id)
    filename = join(request.registry.settings['build.root'],
                    camel_case(build_id), 'Output', filename)
    with open(filename, 'rb') as hdl:
        return '', xmlrpclib.Binary(hdl.read())


# =============================================================================
def output_send_delta(request, context, build_id, filename, sig):
    """Send a delta list of a file of the ``Output`` directory..

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :param filename: (string)
        Name of the file to transfer.
    :param sig: (:class:`xmlrpclib.Binary` instance)
        File signature.
    :return: (tuple)
        ``(<error>, <delta>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    # Send delta
    build_id = _agent_build_id(request, context, build_id)
    filename = join(request.registry.settings['build.root'],
                    camel_case(build_id), 'Output', filename)
    with open(filename, 'rb') as hdl:
        delta_file = DeltaFile(sig.data, hdl)
        delta_buf = delta_file.read()
        delta_file.close()
    return '', xmlrpclib.Binary(delta_buf)


# =============================================================================
def _authorized(request, context):
    """Check if the request is authorized.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :return: (boolean)
        ``True`` if authorized.
    """
    return request.registry['abuild'].authorized_front(
        context['front_id'], context['password'])


# =============================================================================
def _not_authorized(context):
    """Return ``('Not authozied!', '')`` where error message is translated.

    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :return: (tuple)
    """
    return _error(context, _('Not authorized!'))


# =============================================================================
def _error(context, text):
    """Return ``(text, '')`` where error message ``text`` is translated.

    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param text: (string)
        Error message to trnaslate.
    :return: (tuple)
    """
    return localizer(context['lang']).translate(text), ''


# =============================================================================
def _agent_build_id(request, context, build_id):
    """Prefix ``build_id`` with ``front_id`` if agent is not called locally.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :return: (string)
    """
    if request.registry.settings['uid'] != context['front_id']:
        return '%s-%s' % (context['front_id'].lower(), build_id)
    return build_id


# =============================================================================
def _agent_paths(request, context, *files):
    """Prefix files if agent is not called locally.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param files: (list)
        List of files on front in storage.
    :return: (list)
    """
    if request.registry.settings['uid'] != context['front_id']:
        prefix = camel_case(context['front_id'])
        return ['%s-%s' % (prefix, name) for name in files]
    return files


# =============================================================================
def _agent_method(request, context, build_id, method):
    """Check authentification and return Agent ``method`` result.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param context: (dictionary)
        See :meth:`~.lib.build.front.FrontBuildManager.call`.
    :param build_id: (string)
        Build ID.
    :return: (tuple)
        ``(<error>, <method_result>)``
    """
    if not _authorized(request, context):
        return _not_authorized(context)

    build_id = _agent_build_id(request, context, build_id)
    return '', getattr(request.registry['abuild'], method)(build_id)
