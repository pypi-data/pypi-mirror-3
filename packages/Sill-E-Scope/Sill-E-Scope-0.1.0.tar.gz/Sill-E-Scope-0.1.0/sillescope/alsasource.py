#! /usr/bin/env python
"""Linux ALSA data-source for the oscilliscope"""
import os,sys,time,errno
import alsaaudio
from sillescope import nb

class ALSASource( object ):
    input = None
    FRAMES = 160
    FORMAT_MAP = {
        # TODO: should use *native* format, based in architecture,
        # this will break on big-endian machines...
        alsaaudio.PCM_FORMAT_U16_LE: {
            'size': 2,
            'dtype': 'H',
        },
        alsaaudio.PCM_FORMAT_U8: {
            'size': 1,
            'dtype': 'B',
        }
    }
    def __init__( self, device = 'default', format = alsaaudio.PCM_FORMAT_U16_LE, rate=8000 ):
        self.device = device 
        self.format = format 
        self.rate = rate
    def __call__( self, ):
        """Yield ring-buffer with captured data as often as is called"""
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, self.device)
        # configure the input for our needs...
        inp.setchannels(1)
        format = self.format 
        sample_size = self.FORMAT_MAP[ format ]['size']
        dtype = self.FORMAT_MAP[ format ]['dtype']
        inp.setrate( self.rate )
        #print 'format', format
        inp.setformat(format)
        inp.setperiodsize(self.FRAMES)
        
        # Okay, start iterating...
        while True:
            l, data = inp.read()
            if l:
                yield data
            else:
                yield None

def main():
    a = ALSASource( format=alsaaudio.PCM_FORMAT_U8 )
    delay = 1./a.rate
    assert nb.set_non_blocking( sys.stdout )
    for block in a():
        if not block:
            time.sleep( delay )
        while block:
            try:
                sys.stdout.write( block )
            except IOError, err:
                if err.args[0] in (errno.EAGAIN,errno.EWOULDBLOCK):
                    pass 
                elif err.args[0] in (errno.EPIPE,):
                    return
                else:
                    raise
            else:
                block = None

if __name__ == "__main__":
    main()
