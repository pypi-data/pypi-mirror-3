#! /usr/bin/env python
"""A Trivial oscilliscope test in Python"""
import numpy
import os,sys,time
#from OpenGL.GL import *
import threading
from sillescope import alsasource

def main():
    """Run the whole shebang"""
    import pygame 
    source = alsasource.ALSASource( format=alsasource.alsaaudio.PCM_FORMAT_U8 )
    # X captures per view, X*(1/8000)
    asize = source.FRAMES*4
    screen = pygame.display.set_mode( (asize,256))
    running = True 
    ring_buffer = numpy.zeros( (asize,2), dtype='H' )
    ring_buffer_index = numpy.arange( 0, len(ring_buffer), 1, dtype='H' )
    ring_buffer[:,0] = ring_buffer_index 
    read = source( ring_buffer[:,1] )
    while running:
        read.next()
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False
        screen.fill((0, 0, 0))
        pygame.draw.lines(screen, (0, 0, 255), False, ring_buffer )
        pygame.display.flip()
    return source

if __name__ == "__main__":
    data = main()
