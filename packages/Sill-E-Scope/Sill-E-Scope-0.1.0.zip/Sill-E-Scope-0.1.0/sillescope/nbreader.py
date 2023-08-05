"""Non-blocking read-from-file handler..."""
import os,sys,time,errno
import threading
from sillescope import nb

class NBReader( object ):
    """Read from socket/file-like object with non-blocking reads"""
    def __init__( self, handle ):
        assert nb.set_non_blocking( handle ), """Unable to set source to non-blocking mode"""
        self.handle = handle 
    def __call__( self, size=2, max_reads=128 ):
        """Iteratively return blocks of multiples of size

        size -- component size (i.e. sample size)
        max_size -- maximum number of samples to yield before yielding None 
            to allow the rendering process to continue; this will generally 
            need to be pretty high, as there's a lot of overhead associated with 
            adding new items...
        """
        remainder = ""
        while True:
            stop_size = max_reads * size 
            try:
                new = self.handle.read( stop_size )
            except IOError, err:
                if err.args[0] in (errno.EAGAIN,errno.EWOULDBLOCK):
                    yield None
                else:
                    raise
            else:
                if remainder:
                    new = remainder + new 
                odd = len(new)%size
                if odd:
                    remainder = new[-odd:]
                    new = new[:-odd]
                else:
                    remainder = ""
                yield new 
