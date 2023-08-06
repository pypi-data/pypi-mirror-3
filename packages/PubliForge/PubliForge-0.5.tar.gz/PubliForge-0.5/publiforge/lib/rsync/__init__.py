# $Id: __init__.py a8f1b45b2ed8 2011/12/10 10:19:48 patrick $
"""Provides a high-level interface to some librsync functions.

This is a python wrapper around the lower-level _librsync module,
which is written in C.
"""

import types
import array
from os.path import getsize

from ...lib.rsync import _librsync

BLOCKSIZE = _librsync.RS_JOB_BLOCKSIZE


# =============================================================================
class LikeFile(object):
    """File-like object used by SigFile, DeltaFile, and PatchFile."""

    # This will be replaced in subclasses by an object with
    # appropriate cycle() method
    maker = None
    mode = 'rb'

    # -------------------------------------------------------------------------
    def __init__(self, infile, need_seek=None):
        """LikeFile initializer - zero buffers, set eofs off."""
        self.check_file(infile, need_seek)
        self.infile = infile
        self.closed = self.infile_closed = None
        self.inbuf = ""
        self.outbuf = array.array('c')
        self.eof = self.infile_eof = None

    # -------------------------------------------------------------------------
    @classmethod
    def check_file(cls, likefile, need_seek=None):
        """Raise type error if ``likefile`` doesn't have necessary attributes.
        """
        if not hasattr(likefile, 'read'):
            raise TypeError('Basis file must have a read() method')
        if not hasattr(likefile, 'close'):
            raise TypeError('Basis file must have a close() method')
        if need_seek and not hasattr(likefile, 'seek'):
            raise TypeError('Basis file must have a seek() method')

    # -------------------------------------------------------------------------
    def read(self, length=-1):
        """Build up self.outbuf, return first length bytes."""
        if length == -1:
            while not self.eof:
                self._add_to_outbuf_once()
            real_len = len(self.outbuf)
        else:
            while not self.eof and len(self.outbuf) < length:
                self._add_to_outbuf_once()
            real_len = min(length, len(self.outbuf))

        return_val = self.outbuf[:real_len].tostring()
        del self.outbuf[:real_len]
        return return_val

    # -------------------------------------------------------------------------
    def _add_to_outbuf_once(self):
        """Add one cycle's worth of output to self.outbuf."""
        if not self.infile_eof:
            self._add_to_inbuf()
        try:
            self.eof, len_inbuf_read, cycle_out = self.maker.cycle(self.inbuf)
        except _librsync.librsyncError, err:
            raise LibRSyncError(str(err))
        self.inbuf = self.inbuf[len_inbuf_read:]
        self.outbuf.fromstring(cycle_out)

    # -------------------------------------------------------------------------
    def _add_to_inbuf(self):
        """Make sure len(self.inbuf) >= BLOCKSIZE."""
        assert not self.infile_eof
        while len(self.inbuf) < BLOCKSIZE:
            new_in = self.infile.read(BLOCKSIZE)
            if not new_in:
                self.infile_eof = 1
                assert not self.infile.close()
                self.infile_closed = 1
                break
            self.inbuf += new_in

    # -------------------------------------------------------------------------
    def close(self):
        """Close infile."""
        if not self.infile_closed:
            assert not self.infile.close()
        self.closed = 1


# =============================================================================
class SigFile(LikeFile):
    """File-like object which incrementally generates a librsync signature"""

    # -------------------------------------------------------------------------
    def __init__(self, infile, blocksize=BLOCKSIZE):
        """SigFile initializer - takes basis file.

        basis file only needs to have read() and close() methods.  It
        will be closed when we come to the end of the signature.

        """
        LikeFile.__init__(self, infile)
        try:
            self.maker = _librsync.new_sigmaker(blocksize)
        except _librsync.librsyncError, err:
            raise LibRSyncError(str(err))


# =============================================================================
class DeltaFile(LikeFile):
    """File-like object which incrementally generates a librsync delta."""

    # -------------------------------------------------------------------------
    def __init__(self, signature, new_file):
        """DeltaFile initializer - call with signature and new file

        Signature can either be a string or a file with read() and
        close() methods.  New_file also only needs to have read() and
        close() methods.  It will be closed when self is closed.

        """
        LikeFile.__init__(self, new_file)
        if type(signature) is types.StringType:
            sig_string = signature
        else:
            self.check_file(signature)
            sig_string = signature.read()
            assert not signature.close()
        try:
            self.maker = _librsync.new_deltamaker(sig_string)
        except _librsync.librsyncError, err:
            raise LibRSyncError(str(err))


# =============================================================================
class PatchedFile(LikeFile):
    """File-like object which applies a librsync delta incrementally."""

    # -------------------------------------------------------------------------
    def __init__(self, basis_file, delta_file):
        """PatchedFile initializer - call with basis delta

        Here basis_file must be a true Python file, because we may
        need to seek() around in it a lot, and this is done in C.
        delta_file only needs read() and close() methods.

        """
        LikeFile.__init__(self, delta_file)
        if type(basis_file) is not types.FileType:
            raise TypeError("basis_file must be a (true) file")
        try:
            self.maker = _librsync.new_patchmaker(basis_file)
        except _librsync.librsyncError, err:
            raise LibRSyncError(str(err))


# =============================================================================
class LibRSyncError(Exception):
    """Signifies error in internal librsync processing (bad signature, etc.)

    underlying _librsync.librsyncError's are regenerated using this
    class because the C-created exceptions are by default
    unPickleable.  There is probably a way to fix this in _librsync,
    but this scheme was easier.
    """
    pass


# =============================================================================
def get_block_size(filename):
    """
    Return a reasonable block size to use on files of length file_len

    If the block size is too big, deltas will be bigger than is
    necessary. If the block size is too small, making deltas and
    patching can take a really long time.
    """
    file_len = getsize(filename)
    if file_len < 1024000:
        return 512  # set minimum of 512 bytes
    else:
        # Split file into about 2000 pieces, rounding to 512
        file_blocksize = long((file_len / (2000 * 512)) * 512)
        return min(file_blocksize, 2048L)
