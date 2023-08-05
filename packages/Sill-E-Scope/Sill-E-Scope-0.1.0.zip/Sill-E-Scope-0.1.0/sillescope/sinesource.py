#! /usr/bin/env python
import numpy, sys,time, math, errno
import select
from sillescope import nb

def main():
    
    sample_frequency = 8000
    signal_frequency = 500
    signal_amplitude = .5
    
    delay = float(1)/sample_frequency
    nb.set_non_blocking( sys.stdout )
    while True:
        t = time.time() * signal_frequency
        try:
            value = (((numpy.sin( t )*signal_amplitude + 1.0)/2.0)*2**8).astype('B')
            sys.stdout.write( value.tostring() )
        except IOError, err:
            if err.args[0] in (errno.EAGAIN,errno.EWOULDBLOCK):
                pass 
            elif err.args[0] in (errno.EPIPE,):
                return
            else:
                raise
        time.sleep( delay )
#        
#    
#    sine = numpy.sin( numpy.arange( 0,math.pi * 12, 12/128., dtype='f' ) )
#    #sine = sine/10.
#    sine = (sine + 1.0) / 2.0
#    sine = sine * (2**8)
#    elements = len(sine)
#    delay = 1/8000.
#    sine = sine.astype('B').tostring()
#    nb.set_non_blocking( sys.stdout )
#    block = 64
#    while True:
#        to_write = sine
#        while to_write:
#            try:
#                sys.stdout.write( to_write[:block] )
#            except IOError, err:
#                if err.args[0] in (errno.EAGAIN,errno.EWOULDBLOCK):
#                    pass 
#                elif err.args[0] in (errno.EPIPE,):
#                    return
#                else:
#                    raise
#            else:
#                #time.sleep( delay )
#                to_write = to_write[block:]

if __name__ == "__main__":
    main()
