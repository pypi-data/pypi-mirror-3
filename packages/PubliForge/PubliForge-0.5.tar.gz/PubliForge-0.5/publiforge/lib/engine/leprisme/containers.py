# $Id: containers.py 2846fc9c22b4 2012/02/23 07:19:21 patrick $
"""Container factory management."""

from os import walk, remove
from os.path import exists, join, relpath, isdir
from shutil import rmtree
import zipfile
from subprocess import Popen, PIPE

from ...utils import EXCLUDED_FILES


# =============================================================================
class ZipFactory(object):
    """Class for Zip container."""

    uid = 'Zip'

    # -------------------------------------------------------------------------
    def __init__(self, engine):
        """Constructor method.

        :param engine: (:class:`~.lib.engine.leprisme.Engine` instance)
            Engine object on which it depends.
        """
        self._engine = engine

    # -------------------------------------------------------------------------
    def make(self, fid, output):
        """Make an ePub file.

        :param fid: (string)
            File identifier.
        :param output: (string)
            Full path to output directory.
        :return: (string)
            Full path to zip file.
        """
        filename = join(output, '%s.zip' % fid)
        zip_file = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
        keeptmp = self._engine.build.processing['variables'].get('keeptmp')
        for path, dirs, files in walk(output):
            for name in dirs:
                if name in EXCLUDED_FILES or '~' in name:
                    dirs.remove(name)
            for name in files:
                if not name in EXCLUDED_FILES and not '~' in name \
                       and not name.endswith('.zip'):
                    fullname = join(path, name)
                    zip_file.write(fullname, relpath(fullname, output))
                    if not keeptmp:
                        if isdir(fullname):
                            rmtree(fullname)
                        else:
                            remove(fullname)
        zip_file.close()
        return filename


# =============================================================================
class OcfFactory(object):
    """Class for Open Container Format (OCF) file."""

    uid = 'OCF'

    # -------------------------------------------------------------------------
    def __init__(self, engine):
        """Constructor method.

        :param engine: (:class:`~.lib.engine.leprisme.Engine` instance)
            Engine object on which it depends.
        """
        self._engine = engine

    # -------------------------------------------------------------------------
    def make(self, fid, output):
        """Make an Open Container Format file and check its validity.

        :param fid: (string)
            File identifier.
        :param output: (string)
            Full path to output directory.
        :return: (string)
            Full path to ePub file.
        """
        # Input directory
        root = self._engine.config('container:%s' % self.uid, 'root', '')
        if not exists(join(output, root)):
            self._engine.build.stopped('Unknown file "%s"' % root, 'a_error')
            return
        if not exists(join(output, root, 'mimetype')) \
               or not exists(join(output, root, 'META-INF', 'container.xml')):
            self._engine.build.stopped(
                '%s: incorrect OCF structure' % root, 'a_error')
            return
        root = join(output, root)

        # Create zip file
        ocf_file = join(output,
            self._engine.config('Output', 'format').format(fid=fid))
        zip_file = zipfile.ZipFile(ocf_file, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(join(root, 'mimetype'), 'mimetype', zipfile.ZIP_STORED)
        for path, dirs, files in walk(root):
            for name in dirs:
                if name in EXCLUDED_FILES or '~' in name:
                    dirs.remove(name)
            for name in files:
                if not name in EXCLUDED_FILES  and not '~' in name \
                       and name != 'mimetype':
                    zip_file.write(
                        join(path, name), relpath(join(path, name), root))
        zip_file.close()
        if self._engine.build.stopped():
            return

        # OCF checker
        name = self._engine.config('container:%s' % self.uid, 'checker')
        if not name or \
               not self._engine.build.processing['variables'].get('ocfcheck'):
            return ocf_file

        err = Popen([k.format(ocffile=ocf_file) for k in name.split()],
                   stdout=PIPE, stderr=PIPE).communicate()[1]
        if err:
            remove(ocf_file)
            err = err.replace(output.encode('utf8'), '') .replace('\n', ' ')
            self._engine.build.stopped(err.decode('utf8'), 'a_error')
            return

        return ocf_file
