"""OpenGL 1D texture ring-buffer"""
from OpenGL.GL import *

class RingBufferGL1D( object ):
    """Fed a stream of bytes (representing samples) fill a glTexImage1D with the values"""
    BYTE_SIZES = {
        GL_UNSIGNED_BYTE: 1,
        GL_UNSIGNED_SHORT: 2,
        GL_FLOAT: 4,
    }
    def __init__( self, sample_count = 256, offset=0, DATA_TYPE=GL_UNSIGNED_BYTE ):
        """Initialize the ring buffer"""
        self.sample_count = sample_count
        self.offset = offset 
        self.DATA_TYPE = DATA_TYPE 
        self.SAMPLE_BYTE_SIZE = self.BYTE_SIZES[ self.DATA_TYPE ]
    def write_location( self ):
        return (self.offset/float(self.sample_count))
    def create( self ):
        """Create the initial buffer"""
        glTexImage1D(
            GL_TEXTURE_1D, 
            0,
            GL_LUMINANCE,
            self.sample_count,
            0,
            GL_LUMINANCE,
            self.DATA_TYPE,
            None # create the memory without transfer...
        )
    def add( self, data ):
        """Add new data to the ring buffer"""
        if not data:
            return
        data_length = len(data)
        new_samples = data_length//self.SAMPLE_BYTE_SIZE
        if not new_samples:
            return
        
        extra = None
        new_offset = self.offset + new_samples
        if new_offset > self.sample_count:
            remaining = self.sample_count-self.offset
            if remaining:
                extra = data[remaining:]
                if extra == data:
                    self.offset = 0
                    extra = None
                else:
                    data = data[:remaining]
                    new_samples = remaining
            else:
                self.offset = 0
            new_samples = min((new_samples,self.sample_count))
        glTexSubImage1D( 
            GL_TEXTURE_1D, 
            0,
            self.offset,
            new_samples,
            GL_LUMINANCE,
            self.DATA_TYPE,
            data,
        )
        if extra:
            self.offset = 0
            assert len(extra) < data_length
            self.add( extra )
        else:
            self.offset += new_samples
