PyOpenGL/ALSA Software Oscilloscope

Renders unsigned 16-bit integers from standard-in to an oscilliscope-like display 
rendered via OpenGL/shaders.  Provides a sample 16-bit source using ALSASound on 
Linux machines.

Installation and running:

    virtualenv sillescope-env
    source sillescope-env/bin/activate
    pip install -e bzr+http://bazaar.launchpad.net/~mcfletch/sillescope/trunk/

    alsa-source | sillescope
    sine-source | sillescope 
