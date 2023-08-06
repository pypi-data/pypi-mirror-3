# $Id: iniscript.py ef87ae8aab5a 2012/08/31 16:51:06 patrick $
"""INI scripts management."""

from os import walk
from os.path import join, exists, dirname, basename, splitext, normpath, isabs
from shlex import split
from ConfigParser import ConfigParser
import codecs

from ...utils import _, config_get, execute


MEDIA_EXT = {'image': 'svg png tif tiff jpg jpeg eps gif',
             'audio': 'wav ogg aac ac3 mp3',
             'video': 'dv mpg ogv mp4 mov avi webm flv'}


# =============================================================================
class IniScript(object):
    """Class for INI script managment."""

    # -------------------------------------------------------------------------
    def __init__(self, engine):
        """Constructor method.

        :param engine: (:class:`~.lib.engine.leprisme.Engine` instance)
            Engine object on which it depends.
        """
        self._engine = engine

    # -------------------------------------------------------------------------
    def convert_media(self, output, filename, ini_file):
        """Convert a media (image, audio or video).

        :param output: (string)
            Path to the output directory.
        :param filename: (string)
            Relative path to the original file to transform.
        :param ini_file: (string)
            Path to INI file.
        """
        # Read INI file
        config = ConfigParser({
            'here': dirname(ini_file), 'output': output,
            'filepath': join(self._engine.build.data_path, dirname(filename)),
            'stgpath': self._engine.build.data_path,
            'ext': '{ext}', 'source': '{source}', 'target': '{target}'})
        config.readfp(codecs.open(ini_file, 'r', 'utf8'))

        # Compute full path to source
        data_id = config_get(config, 'Source', 'id')
        data_type = config_get(config, 'Source', 'type')
        source = self._find_media(
            data_type, data_id,
            join(self._engine.build.data_path, dirname(filename)),
            config_get(config, 'Source', 'search'))
        if not source or not exists(source):
            self._engine.build.stopped(_(
                '${f}: no source for "${i}"',
                {'f': basename(ini_file), 'i': data_id}), 'a_error')
            return

        # Read full path to target
        target = config_get(config, 'Target', 'file')
        if not target:
            self._engine.build.stopped(_(
                '${f}: no target', {'f': basename(ini_file)}))
            return

        # Transform data
        section = 'Transformation:%s' % splitext(source)[1][1:]
        if not config.has_section(section):
            section = 'Transformation'
        for step in range(100):
            cmd = config_get(config, section, 'step.%d' % step)
            if cmd:
                cmd = cmd.format(source=source, target=target)
                error = execute(split(cmd.encode('utf8')), output)
                if error:
                    self._engine.build.stopped(error[0], 'a_error')
                    self._engine.build.stopped(error[1])
                    return
        if not exists(target):
            self._engine.build.stopped(_(
                '${f}: unable to make "${i}"',
                {'f': basename(ini_file), 'i': data_id}), 'a_error')

    # -------------------------------------------------------------------------
    def post_execution(self, output, ini_file, target_file):
        """Process post INI script.

        :param output: (string)
            Path to the output directory.
        :param ini_file: (string)
            Path to INI file.
        :param target_file: (string)
            Path to target file.
        """
        config = ConfigParser({
            'here': dirname(ini_file), 'output': output,
            'target': target_file})
        config.read(ini_file)

        for step in range(100):
            cmd = config_get(config, 'Transformation', 'step.%d' % step)
            if cmd:
                error = execute(split(cmd.encode('utf8')), output)
                if error:
                    self._engine.build.stopped(error[0], 'a_error')
                    self._engine.build.stopped(error[1])
                    return
        if not exists(target_file):
            self._engine.build.stopped(
                _('${f}: no output', {'f': basename(ini_file)}), 'a_error')

    # -------------------------------------------------------------------------
    def _find_media(self, media_type, media_id, file_path, search):
        """Look for a media.

        :param media_type: (string)
            Type of media (image, audio or video).
        :param media_id: (string)
            Media ID.
        :param file_path: (string)
            Path to file being processed.
        :param patterns: (string)
            List of patterns to check.
        :return: (string)
            Full path to source file or ``None``.
        """
        # Initialize
        # pylint: disable = I0011, R0912
        if media_type not in ('image', 'audio', 'video') or not media_id \
                or not search:
            return
        done = []
        extensions = self._engine.config(
            'Input', '%s_ext' % media_type, MEDIA_EXT[media_type]).split()
        search = [k.strip() for k in search.split(',')]
        roots = [file_path] + [join(self._engine.build.data_path, k) for k in
                               self._engine.build.pack['resources']
                               + self._engine.build.processing['resources']]

        # Local function
        def _look_for(pattern):
            """Look for a source file by trying each extension."""
            for ext in ('{ext}' in pattern and extensions or '-'):
                name = pattern.format(ext=ext)
                if exists(name):
                    return name

        # Browse search list
        for item in search:
            if isabs(item):
                name = _look_for(item)
                if name is not None:
                    return name
                done.append(normpath(item))
            else:
                for root in roots:
                    for path, dirs, name in walk(root):
                        for name in ['.'] + dirs:
                            name = normpath(join(path, name, item))
                            if not name in done:
                                done.append(name)
                                name = _look_for(name)
                                if name is not None:
                                    return name
