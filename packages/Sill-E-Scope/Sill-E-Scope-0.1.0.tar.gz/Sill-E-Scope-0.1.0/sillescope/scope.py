#! /usr/bin/env python
"""OpenGL front-end for Sill-E-Scope"""
import OpenGL
OpenGL.ERROR_ON_COPY = True 
OpenGL.CONTEXT_CHECKING = False 
OpenGL.ALLOW_NUMPY_SCALARS = False 
OpenGL.FORWARD_COMPATIBLE_ONLY = True

from OpenGL.GL import *
from OpenGL.GLUT import *

from OpenGL import constants
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import *
from OpenGL import constants
from sillescope import nbreader
from sillescope import glringbuffer

import time, sys, traceback, optparse
program = None
points = None
texture = None

ring_buffer = None

def collapse( l ):
    result = []
    for x in l:
        result.extend( x )
    return result
FLOAT_5_6 = GLfloat * (5 * 6)
point_array = collapse([
    [-1,-1,0, 0,0],[-1,1,0, 0,1],[1,-1,0, 1,0],
    [1,-1,0, 1,0],[-1,1,0, 0,1],[1,1,0, 1,1],
])
points = vbo.VBO( FLOAT_5_6( *point_array ))

source = nbreader.NBReader( sys.stdin )( size=1, max_reads=128 )

def InitGL(Width, Height):
    glClearColor( .25,.25,.7, 1.0 )
    glDisable( GL_CULL_FACE )
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho( -1.1, 1.1, -1.1, 1.1, -1.1, 1.1 )

    global program
    program = compileProgram(
        compileShader('''
            attribute vec3 Vertex_position;
            attribute vec2 Vertex_tc;
            varying vec2 data_location;
            void main() {
                data_location = Vertex_tc;
                gl_Position = gl_ModelViewProjectionMatrix * vec4(Vertex_position,1.0);
            }
        ''',GL_VERTEX_SHADER),
        compileShader('''
            varying vec2 data_location;
            uniform sampler1D raw_data;
            uniform float write_location;
            void main() {
                vec4 raw_value = texture( raw_data, data_location.x );
                float c = abs(data_location.y - raw_value.r) * 128.;
                gl_FragColor = vec4( c,c,c,.5);
            }
    ''',GL_FRAGMENT_SHADER),)
    glEnablei(GL_BLEND, 0)
    glBlendEquationSeparate(GL_FUNC_ADD, GL_FUNC_ADD)
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO)
    
    global points 
    global texture
    
    texture = glGenTextures(1)
    glActiveTexture( GL_TEXTURE0 + 1 )
    glBindTexture( GL_TEXTURE_1D, texture )
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glPixelStorei(GL_PACK_ALIGNMENT,1)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    # creates the actual buffer on the card...
    ring_buffer.create()
    
    with program:
        global write_location_uniform
        write_location_uniform = glGetUniformLocation( program, "write_location" )
        with points:
            glUniform1i( glGetUniformLocation( program, "raw_data" ), 1 )
            
            vertex_loc = glGetAttribLocation( program, 'Vertex_position' )
            tc_loc = glGetAttribLocation( program, 'Vertex_tc' )
            glEnableVertexAttribArray( vertex_loc )
            glEnableVertexAttribArray( tc_loc )

            stride = 5*4
            glVertexAttribPointer(
                vertex_loc,
                3, GL_FLOAT, False, stride, points
            )
            glVertexAttribPointer(
                tc_loc,
                2, GL_FLOAT, False, stride, points+12
            )

def update_texture( texture ):
    items = []
    try:
        new = source.next()
        while new:
            items.append( new )
            new = source.next()
    except StopIteration, err:
        sys.exit( 0 )
    if items:
        glActiveTexture( GL_TEXTURE0 + 1 )
        glBindTexture( GL_TEXTURE_1D, texture )
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glPixelStorei(GL_PACK_ALIGNMENT,1)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        ring_buffer.add( "".join(items) )
        return texture
    else:
        return None

def ReSizeGLScene(Width, Height):
    if Height == 0:
        Height = 1

    glViewport(0, 0, Width, Height)

def DrawGLScene():
    if update_texture(texture):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        with program:
            write_location = ring_buffer.write_location()
            glUniform1f( write_location_uniform, write_location)
            with points:
                glBindTexture( GL_TEXTURE_1D, texture )
                # TODO: streaming write...
                glDrawArrays( GL_TRIANGLES, 0, len(points) )
        glutSwapBuffers()
    else:
        time.sleep( 0.05 )

FULL_SCREEN = None
def toggleFullScreen():
    global FULL_SCREEN
    if FULL_SCREEN:
        x,y,w,h = FULL_SCREEN
        glutSetWindow( window )
        glutPositionWindow( window, x,y )
        glutReshapeWindow( window, w,h )
        FULL_SCREEN = False
    else:
        FULL_SCREEN = [
            glutGet( GLUT_WINDOW_X ),
            glutGet( GLUT_WINDOW_Y ),
            glutGet( GLUT_WINDOW_WIDTH ),
            glutGet( GLUT_WINDOW_HEIGHT ),
        ]
        glutSetWindow( window )
        glutFullScreen( )

def keyPressed(*args):
    if args[0] == '\x1b':
        sys.exit()
    elif args[0] in ('f','F'):
        toggleFullScreen()
    else:
        print args[0]

def option_parser( ):
    parser = optparse.OptionParser( )
    parser.add_option('--fullscreen', action='store_true', dest='fullscreen',default=False )
    parser.add_option('--width', dest='width',default=800, type='int')
    parser.add_option('--height', dest='height',default=600, type='int')
    
    def resolve_format(option, opt_str, value, parser):
        value = getattr( constants, value, None )
        possible = sorted(glringbuffer.RingBufferGL1D.BYTE_SIZES.keys())
        if value not in possible:
            raise optparse.OptionValueError(
                "Need to specify one of: %s for format"%(possible,)
            )
        parser.values.format = value
    parser.add_option(
        '--format', action='callback', default=GL_UNSIGNED_BYTE, dest='format', 
        callback=resolve_format, type='str' 
    )
    
    return parser

def main():
    """Main loop for the GLUT oscilloscope rendering
    
    TODO: Provide command-line parameters for controlling data-formats so that e.g. 
        raw floats or the like could be sent in over the pipe/socket
    TODO: Use more text-friendly GUI for the presentation (e.g. Pygame)
        TODO: Then add demarcations of values (i.e. 0-1)
    TODO: Eliminate the (pointless) matrix setup calls and just use core OpenGL 
    TODO: Regular app support (window size storage and the like)
    TODO: Interactively allow for zooming into the output...
    """
    global window
    glutInit(sys.argv)
    
    options,args = option_parser().parse_args()

#   Eventually this should be enabled, but for now we're using 
#   the "projection matrix" stuff instead of calculating our own...
#    glutInitContextVersion(3, 2)
#    glutInitContextFlags(GLUT_FORWARD_COMPATIBLE)
#    glutInitContextProfile(GLUT_CORE_PROFILE)
    
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowSize(options.width,options.height)
    glutInitWindowPosition(0, 0)

    window = glutCreateWindow("Sill-E-Scope")
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutReshapeFunc(ReSizeGLScene)
    glutKeyboardFunc(keyPressed)
    if options.fullscreen:
        toggleFullScreen()

    global ring_buffer
    ring_buffer = glringbuffer.RingBufferGL1D( DATA_TYPE=getattr(options,'format',GL_UNSIGNED_BYTE) )
    InitGL(options.width,options.height)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
