# $Id: iniscript.py b1ffa5a75b89 2012/02/19 23:23:01 patrick $
"""INI scripts management."""

from os import walk
from os.path import join, exists, dirname, basename, splitext, normpath
from os.path import getmtime
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE

from ...utils import config_get


MEDIA_EXT = {'image': 'svg png tif tiff jpg jpeg eps gif',
             'audio': 'flac wav ogg ac3 mp3',
             'video': 'dv mpg mov avi flv'}


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
    def execute(self, output, filename, ini_file):
        """Make an ePub file.

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
            'stgpath': self._engine.build.data_path,
            'filepath': join(self._engine.build.data_path, dirname(filename)),
            'id': '{id}', 'ext': '{ext}', 'source': '{source}',
            'target': '{target}'})
        config.read(ini_file)

        # Compute full path to source
        data_id = config_get(config, 'Source', 'id')
        source = config_get(config, 'Source', 'file')
        if source:
            source = source.format(id=data_id)
        if not source or not exists(source):
            data_type = config_get(config, 'Source', 'type')
            if data_type in ('image', 'audio', 'video'):
                source = self._find_media(data_type, data_id,
                    config_get(config, 'Source', 'paths'),
                    config_get(config, 'Source', 'patterns'))
        if not source or not exists(source):
            self._engine.build.stopped('%s: no source for "%s"'
                % (basename(ini_file), data_id), 'a_error')
            return

        # Read full path to target
        target = config_get(config, 'Target', 'file')
        if not target:
            self._engine.build.stopped('%s: no target' % basename(ini_file))
            return

        # Already processed?
        if not self._engine.build.processing['variables'].get('force') \
               and exists(target) and getmtime(target) > getmtime(source):
            return

        # Transform data
        section = 'Transformation:%s' % splitext(source)[1][1:]
        if not config.has_section(section):
            section = 'Transformation'
        for step in range(100):
            cmd = config_get(config, section, 'step.%d' % step)
            if cmd:
                cmd = cmd.format(source=source, target=target).split()
                try:
                    err = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate()[1]
                except OSError, err:
                    self._engine.build.stopped(err)
                if not exists(target):
                    self._engine.build.stopped(err, 'a_error')
                    return
            if self._engine.build.stopped():
                return

    # -------------------------------------------------------------------------
    def _find_media(self, media_type, media_id, sources, patterns):
        """Look for a media.

        :param media_type: (string)
            Type of media (image, audio or video).
        :param media_id: (string)
            Media ID.
        :param sources: (string)
            List of source paths to browse.
        :param patterns: (string)
            List of patterns to check.
        :return: (string)
            Full path to source file or ``None``.
        """
        # pylint: disable = I0011, R0912
        if not media_id or not sources or not patterns:
            return

        # Get extension, path and pattern list
        extensions = self._engine.config(
            'Input', '%s_ext' % media_type, MEDIA_EXT[media_type]).split()
        sources = [normpath(k.strip()) for k in sources.split(',')]
        patterns = [k.strip() for k in patterns.split(',')]
        done = []

        # Local function
        def look_in_directory(source):
            """Look for a source in a directory."""
            for pattern in patterns:
                if '{ext}' not in pattern:
                    name = join(source, pattern.format(id=media_id))
                    if exists(name):
                        return name
                    continue
                for ext in extensions:
                    name = join(source, pattern.format(id=media_id, ext=ext))
                    if exists(name):
                        return name

        # Look for media in sources
        for source in sources:
            name = look_in_directory(source)
            if name is not None:
                return name
            for path, dirs, name in walk(source):
                for name in dirs:
                    name = normpath(join(path, name))
                    if name in done:
                        continue
                    done.append(name)
                    name = look_in_directory(name)
                    if name is not None:
                        return name
            done.append(source)
