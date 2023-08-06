# $Id: containers.py e2c913b1a1e3 2012/09/09 19:47:40 patrick $
"""Container factory management."""

from os import walk, remove
from os.path import exists, join, relpath, isdir, basename, dirname, splitext
from shutil import rmtree
import zipfile
from lxml import etree

from ...utils import _, EXCLUDED_FILES, get_mime_type, execute
from ...xml import load


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
            self._engine.build.stopped(
                _('unknown directory "${d}"', {'d': root}), 'a_error')
            return
        if not exists(join(output, root, 'mimetype')) \
                or not exists(join(output, root, 'META-INF', 'container.xml')):
            self._engine.build.stopped(_('incorrect OCF structure'), 'a_error')
            return
        root = join(output, root)

        # Update manifest
        manifest = self._engine.config('container:%s' % self.uid, 'manifest')
        if manifest and not self._update_manifest(root, manifest):
            return

        # Create zip file
        ocf_file = join(
            output, self._engine.config('Output', 'format').format(fid=fid))
        zip_file = zipfile.ZipFile(ocf_file, 'w', zipfile.ZIP_DEFLATED)
        zip_file.write(join(root, 'mimetype'), 'mimetype', zipfile.ZIP_STORED)
        for path, dirs, files in walk(root):
            for name in dirs:
                if name in EXCLUDED_FILES or '~' in name:
                    dirs.remove(name)
            for name in files:
                if not name in EXCLUDED_FILES and not '~' in name \
                        and name != 'mimetype':
                    zip_file.write(
                        join(path, name), relpath(join(path, name), root))
        zip_file.close()
        if self._engine.build.stopped():
            return

        # Check validity
        if self._check_validity(output, ocf_file):
            return ocf_file

    # -------------------------------------------------------------------------
    def _update_manifest(self, root, manifest):
        """Update file list in manifest tag.

        :param root: (string)
            Full path to root directory.
        :param manifest: (string)
            A string such as ``<relative_path_to_opf>:<xpath_to_manifest>``.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Read manifest node
        # pylint: disable = I0011, E1103
        opf_file = join(root, manifest.partition(':')[0])
        tree = load(opf_file)
        if isinstance(tree, basestring):
            self._engine.build.stopped(tree, 'a_error')
            return False
        root = dirname(opf_file)
        xpath = manifest.partition(':')[2].strip()
        manifest_elt = tree.xpath(
            xpath, namespaces={'opf': tree.getroot().tag.split('}')[0][1:]})
        if len(manifest_elt) != 1:
            self._engine.build.stopped(
                _('${x}: incorrect XPATH', {'x': xpath}), 'a_error')
            return
        manifest_elt = manifest_elt[0]

        # Browse declared files
        done = [basename(opf_file)]
        for elt in manifest_elt.iterchildren(tag=etree.Element):
            done.append(elt.get('href'))

        # Browse real files
        modified = False
        for path, name, files in walk(root):
            for name in files:
                relname = relpath(join(path, name), root)
                if relname in done or name in EXCLUDED_FILES or '~' in name:
                    continue
                elt = etree.SubElement(
                    manifest_elt, 'item', id='x_%s' % splitext(name)[0],
                    href=relname)
                elt.set('media-type', get_mime_type(join(path, name))[0])
                elt.tail = '\n    '
                modified = True

        # Save modified file
        if modified:
            tree.write(opf_file, encoding='utf-8', xml_declaration=True,
                       pretty_print=True)
        return True

    # -------------------------------------------------------------------------
    def _check_validity(self, output, ocf_file):
        """Check OCF file validity.

        :param output: (string)
            Full path to ouput directory.
        :param ocf_file: (string)
            Full path to OCF file to check.
        :return: (boolean)
            ``True`` if succeeds.
        """
        name = self._engine.config('container:%s' % self.uid, 'checker')
        if not name or \
                not self._engine.build.processing['variables'].get('ocfcheck'):
            return True

        error = execute(
            [k.format(ocffile=ocf_file) for k in name.split()], output,
            'idml' in name)
        if error:
            remove(ocf_file)
            error = error[0] or error[1]
            error = error.replace(output, '').replace('\n', ' ')
            self._engine.build.stopped(error, 'a_error')
            return False

        return True
