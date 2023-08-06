# $Id: utils.py 7af639d5ec56 2012/03/18 16:06:23 patrick $
"""Some various utilities."""

import sys
from os import sep, listdir, makedirs
from os.path import exists, join, isdir, dirname
import shutil
import re
import zipfile
import mimetypes
from datetime import datetime
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from cStringIO import StringIO
from beaker.crypto.util import sha1

from pyramid.i18n import TranslationStringFactory, make_localizer


_ = TranslationStringFactory('publiforge')
EXCLUDED_FILES = ('.hg', '.svn', '.git', 'Thumbs.db', '.DS_Store')
FILE_TYPES = ('css', 'csv', 'epub+zip', 'folder', 'html', 'jpeg', 'mpeg',
    'msword', 'ogg', 'pdf', 'plain', 'png', 'postscript', 'relaxng', 'tiff',
    'vnd.ms-excel', 'vnd.oasis.opendocument.spreadsheet',
    'vnd.oasis.opendocument.text', 'x-msdos-program', 'x-msvideo', 'x-python',
    'x-shockwave-flash', 'x-tar', 'x-wav', 'xml', 'xml-dtd', 'zip')
TEXT_TYPES = ('css', 'csv', 'html', 'plain', 'relaxng', 'x-python', 'xml',
    'xml-dtd')


# =============================================================================
def localizer(locale_name, directories=None):
    """Create a :class:`pyramid.i18n.Localizer` object corresponding to the
    provided locale name from the translations found in the list of translation
    directories.

    :param locale_name: (string)
        Current language.
    :param directories: (list, optional)
        Translation directories.
    :return: (:class:`pyramid.i18n.Localizer` instance)
    """
    return make_localizer(
        locale_name, directories or [join(dirname(__file__), '..', 'Locale')])


# =============================================================================
def has_permission(request, *perms):
    """Check if the user has at least one of the specified permissions.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param perms: (list)
        List of permission groups.
    :return: (boolean)

    See :ref:`frontreference_permissions`.
    """
    if not 'perms' in request.session:
        return False
    if 'admin' in request.session['perms']:
        return True
    for perm in perms:
        if perm in request.session['perms'] \
               or '%s_manager' % perm[0:3] in request.session['perms']\
               or ('%s_editor' % perm[0:3] in request.session['perms']
                   and perm[4:] == 'user'):
            return True
    return False


# =============================================================================
def config_get(config, section, option, default=None):
    """Retrieve a value from a configuration object.

    :param config: (object)
        Configuration object.
    :param section: (string)
        Section name.
    :param option: (string)
        Option name.
    :param default: (string, optional)
        Default value
    :return: (string)
        Read value or default value.
    """
    if not config.has_option(section, option):
        return default
    value = config.get(section, option)
    return (isinstance(value, str) and value.decode('utf8')) or value


# =============================================================================
def copy_content(src_dir, dst_dir, exclude=EXCLUDED_FILES):
    """Copy the content of a ``src_dir`` directory into a ``dst_dir``
    directory.

    :param src_dir: (string)
        Source directory path.
    :param dst_dir: (string)
        Destination directory path.
    :param exclude: (list)
        List of files to exclude.
    """
    if not exists(dst_dir):
        makedirs(dst_dir)
    for name in listdir(src_dir):
        if name in exclude:
            continue
        fullname = join(src_dir, name)
        if not isinstance(fullname, unicode):
            fullname = fullname.decode('utf8')
            name = name.decode('utf8')
        if isdir(fullname):
            copy_content(fullname, join(dst_dir, name), exclude)
        else:
            shutil.copy(fullname, dst_dir)


# =============================================================================
def camel_case(text):
    """Convert ``text`` in Camel Case."""
    if sys.version_info[:3] >= (2, 7, 0):
        # pylint: disable = I0011, E1123
        return re.sub(r'(^\w|[-_ 0-9]\w)',
            lambda m: m.group(0).replace('_', '').replace(' ', '').upper(),
            text, flags=re.UNICODE)
    else:
        return re.sub(r'(^\w|[-_ 0-9]\w)',
            lambda m: m.group(0).replace('_', '').replace(' ', '').upper(),
            text)


# =============================================================================
def normalize_name(name):
    """Normalize name."""
    return re.sub(r'[*?"\'/]', '_', u'_'.join(name.strip().split()))\
           .lower().encode('utf8')


# =============================================================================
def hash_sha(value, key):
    """Cryptographic hash function with SHA1 algorithm.

    :param value: (string)
        String to hash.
    :param key: (string)
        Encryption key.
    """
    return sha1('%s%s' % (value.encode('utf8'), key)).hexdigest()


# =============================================================================
def encrypt(value, key):
    """Encryption function.

    :param value: (string)
        String to encrypt.
    :param key: (string)
        Encryption key.
    :return: (string)
        Encrypted value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        return b64encode(cipher.encrypt(value + ' ' * (16 - len(value) % 16)))


# =============================================================================
def decrypt(value, key):
    """Decryption function.

    :param value: (string)
        String to decrypt.
    :param key: (string)
        Encryption key.
    :return: (string)
        Clear value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        return cipher.decrypt(b64decode(str(value))).strip()


# =============================================================================
def zipize(data_list, are_files):
    """Return a ZIP archive containing all data of ``data_list``.

    :param data_list: (list)
        A list of tuples such as ``(<filename_in_zip>, <string_or_filename>)``.
    :param are_files: (boolean)
        ``True`` if strings represent file name.
    :return: (ZIP)
    """
    output = StringIO()
    zip_file = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    for data in data_list:
        if not are_files:
            zip_file.writestr(data[0], data[1])
    zip_file.close()

    return output.getvalue()


# =============================================================================
def unzip(archive, outpath):
    """Extract an archive ignoring forbidden files.

    :param archive: (string or file)
        Name of the ZIP file.
    :param outpath: (string)
        Full path where extract the archive.
    """
    zip_file = zipfile.ZipFile(archive, 'r')
    for zipinfo in zip_file.infolist():
        if not [k for k in EXCLUDED_FILES
                if ('%s%s' % (sep, k)) in zipinfo.filename]:
            zip_file.extract(zipinfo, outpath)


# =============================================================================
def get_mime_type(filename):
    """Return the mime type of ``filename``.

    :param filename: (string)g
        File name.
    :return: (tuple)
        A tuple such as ``(mime_type, subtype)``. For instance:
        ``('text/plain', 'plain')``.
    """
    if isdir(filename):
        return 'folder', 'folder'
    mimetype = mimetypes.guess_type(filename, False)[0]
    if mimetype is None:
        return 'unknown', 'unknown'
    subtype = mimetype.partition('/')[2]
    return mimetype, subtype or mimetype


# =============================================================================
def size_label(size, is_dir):
    """Return a size in o, Kio, Mio or Gio.

    :param size: (integer)
        Size in figures.
    :param is_dir: (boolean)
        ``True`` if it is about a directory.
    :return: (string or :class:`pyramid.i18n.TranslationString`)
    """
    # For a directory
    if is_dir:
        return _('${n} items', {'n': size}) if size > 1 else \
               _('${n} item', {'n': size})

    # For a file
    if size >= 1073741824:
        return '%.1f Gio' % round(size / 1073741824.0, 1)
    elif size >= 1048576:
        return '%.1f Mio' % round(size / 1048576.0, 1)
    elif size >= 1024:
        return '%.1f Kio' % round(size / 1024.0, 1)
    return '%d o' % size


# =============================================================================
def age(mtime):
    """Return an age in minutes, hours, days or date.

    :param mtime: (datetime)
        Modification time.
    :return: (:class:`pyramid.i18n.TranslationString` or string)
        Return an age or a date if ``mtime`` is older than a year.
    """
    # pylint: disable = I0011, R0911
    if not mtime:
        return ''
    delta = datetime.now() - mtime
    if delta.days == 0 and delta.seconds < 60:
        return _('1 second') if delta.seconds <= 1 \
               else _('${s} seconds', {'s': delta.seconds})
    elif delta.days == 0 and delta.seconds < 3600:
        minutes = delta.seconds / 60
        return _('1 minute') if minutes == 1 \
               else _('${m} minutes', {'m': minutes})
    elif delta.days == 0:
        hours = delta.seconds / 3600
        return _('1 hour') if hours == 1 \
               else _('${h} hours', {'h': hours})
    elif delta.days < 7:
        return _('1 day') if delta.days == 1 \
               else _('${d} days', {'d': delta.days})
    elif delta.days < 30:
        weeks = delta.days / 7
        return _('1 week') if weeks == 1 \
               else _('${w} weeks', {'w': weeks})
    elif delta.days < 365:
        months = delta.days / 30
        return _('1 month') if months == 1 else \
               _('${m} months', {'m': months})
    return str(mtime.replace(microsecond=0))[0:-9]


# =============================================================================
def cache_key(cache, method_name, *args):
    """Compute a cache key.

    :param cache: (:class:`beaker.cache.Cache` instance)
    :param method_name: (string)
    :param args: (positional arguments)
    :return: (string)
    """
    # pylint: disable = I0011, W0141
    try:
        key = ','.join(map(str, args))
    except UnicodeEncodeError:
        key = ','.join(map(unicode, args))
    key = '%s(%s)' % (method_name, key)
    if len(key) + len(cache.namespace_name) > 250:
        key = sha1(key).hexdigest()
    return key


# =============================================================================
def cache_method():
    """Decorator to cache a method of a class with ``self.cache`` attribute.

    ``self.cache`` is a :class:`beaker.cache.Cache` instance.

    The method being decorated must only be called with positional arguments,
    and the arguments must support being stringified with ``str()``.
    """
    def _wrapper(create_method):
        """Wrapper function."""

        def _cached(self, *args):
            """Cache function."""
            if not hasattr(self, 'cache'):
                raise Exception('Class must have a "cache" attribute!')
            key = cache_key(self.cache, create_method.__name__, *args)

            def _createfunc():
                """Creation function."""
                # pylint: disable = I0011, W0142
                return create_method(self, *args)

            return self.cache.get_value(key, createfunc=_createfunc)

        return _cached

    return _wrapper
