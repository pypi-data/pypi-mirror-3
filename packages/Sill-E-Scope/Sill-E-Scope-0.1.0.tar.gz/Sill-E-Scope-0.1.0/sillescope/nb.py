"""Function to set an existing file-handle non-blocking"""
import os,sys,time,fcntl,errno
import threading

def set_non_blocking( fh ):
    if isinstance( fh, int ) or hasattr( fh, 'fileno' ):
        flags = fcntl.fcntl(fh, fcntl.F_GETFL)
        fcntl.fcntl(fh, fcntl.F_SETFL, flags| os.O_NONBLOCK)
        return True 
    else:
        return False
