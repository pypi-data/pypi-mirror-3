#! /usr/bin/env python
"""Setup Sill-E-Scope"""
from setuptools import setup
import os

version = [
    (line.split('=')[1]).strip().strip('"').strip("'")
    for line in open(os.path.join('sillescope', '__init__.py'))
    if line.startswith( '__version__' )
][0]

if __name__ == "__main__":
    setup (
        name = "Sill-E-Scope",
        version = version,
        url = "https://launchpad.net/sillescope",
        download_url = "",
        description = "Trivial Software Oscilloscope",
        author = "Mike C. Fletcher",
        author_email = "mcfletch@vrplumber.com",
        install_requires = [
            'PyOpenGL',
            'pyalsaaudio',
            #'numpy',
        ],
        license = "BSD",
        package_dir = {
            'sillescope':'sillescope',
        },
        packages = [
            'sillescope',
        ],
        options = {
            'sdist':{
                'force_manifest':1,
                'formats':['gztar','zip'],},
        },
        zip_safe=False,
        entry_points = {
            'console_scripts': [
                'alsa-source=sillescope.alsasource:main',
                'sine-source=sillescope.sinesource:main',
            ],
            'gui_scripts': [
                'sillescope=sillescope.scope:main',
            ],
        },
        classifiers = [
            """License :: OSI Approved :: BSD License""",
            """Programming Language :: Python""",
            """Intended Audience :: Education""",
        ],
        keywords = 'Oscilloscope,PyOpenGL,OpenGL,ALSA',
        long_description = """Renders ALSA audio samples into an oscilloscope-like display

This is a demonstration project which renders ALSA audio samples (16-bit integer streams) using (core) OpenGL. It is intended to serve as sample code for setting up shader-based rendering of basic data-sets (in this case, a ring-buffer of 16-bit integers). The code is currently just "get it done" level, without worrying about efficiency or best-practice coding.

Development targets include the ability to zoom in on the sample data set (i.e. use a matrix to multiply the data being presented), the ability to mark/calibrate the display, adding more data-sources, and cleaning up the code.""",
        platforms = ['Linux'],
    )
    
