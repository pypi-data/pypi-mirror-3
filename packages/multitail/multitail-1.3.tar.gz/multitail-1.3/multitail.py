"""Python generator which implements `tail -f`-like behaviour, with support for tailing multiple files."""

import time
import os


def tail(filename, **opts):
    """Simple "tail -f"-like tailer""" 
    for _, line in multitail([filename], **opts):
        yield line
        

def multitail(filenames, tail_from_start=False):
    """ Simple "tail -f"-like tailer for multiple files
        
        Yields pairs (filename, line)
    """ 
    files = [_TailedFile(x).ensure_exists() for x in filenames]
    if not tail_from_start:
        for f in files:
            f.seek_end()
            
    while 1:
        got_line = False
        for f in files:
            line = f.readline()
            if not line:
                continue
            else:
                got_line = True
                yield f.fn, line
        if not got_line:
            time.sleep(1)
            for f in files:
                if f.is_rotated():
                    f.reopen()


class _TailedFile(object):
    def __init__(self, fn):
        self.fn = fn
        self._obj = None

    @property
    def obj(self):
        try:
            if self._obj is None:
                self._obj = open(self.fn)
                self._ino = os.fstat(self._obj.fileno()).st_ino          
            return self._obj
        except IOError:
            return None

    def ensure_exists(self):
        if not self.obj:
            raise IOError('Failed to open file %r' % self.fn)
        return self

    def is_rotated(self):
        try:
            return os.stat(self.fn).st_ino != self._ino
        except OSError:
            return True

    def reopen(self):
        self._obj = None
        self._ino = None

    def seek_end(self):
        self.obj.seek(0, 2)

    def readline(self):
        if not self.obj:
            return None

        where = self.obj.tell()
        line = self.obj.readline()
        if not line:
            self.obj.seek(where)
            return None
        return line

    def __repr__(self):
        return '%r' % self.fn
