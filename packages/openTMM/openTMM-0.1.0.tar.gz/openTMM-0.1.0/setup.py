'''
setup.py - Setup script for openTMM
Copyright (c) 2010, Alex J. Yuffa <ayuffa@gmail.com>

This library is free software; you can redistribute it and/or
modify it under the terms of The MIT License, 
http://www.opensource.org/licenses/mit-license.php
'''
__version__ = '0.1.0'

# Fake python into thinking that we are using setuptools and not distutils from numpy.
import  setuptools 
from numpy.distutils.core import Extension
from numpy.distutils.core import setup

NAME = "openTMM"
VERSION = __version__
DESCRIPTION = "Electrodynamic S-matrix Code"
LONG_DESCRIPTION = """
openTMM is an object-oriented electrodynamic S-matrix (transfer matrix) code with modern applications.

Electromagnetic wave propagation through planar stratified media (multilayer stack); the three-dimensional space is divided into layers.  The interfaces separating the layers are assumed to be perfectly planar and the layers are assumed to be isotropic and homogeneous, with a complex permittivity and permeability.  Moreover, the layers may be composed of a left-handed material (negative refractive material) and/or a right-handed material.  The implementation is suitable for the study of modern applications, e.g., Anderson localization of light and sub-wavelength imaging.

For more details see our preprint, openTMMpreprint.pdf, which is distributed with the source code.


MAJOR CHANGES IN VERSION 0.1.0:

1.  Changed standard transfer matrix alg. to S-matrix alg.  The solution should now be numerically stable in presence of large absorption.

2.  Rewrote openTMMpreprint.pdf.  It now includes a discussion of different transfer matrix algorithms and performance comparison of python to Fortran 90/95 as well as numerical stability tests.
"""
AUTHOR = 'Alex J. Yuffa'
AUTHOR_EMAIL = 'ayuffa@gmail.com'
URL = 'http://mesoscopic.mines.edu/mediawiki/index.php/Free_Python_codes'
LICENSE = 'The MIT License'
PLATFORMS = ['Linux', 'Unix', 'Mac OS X', 'Windows']
PACKAGE_DIR = {'openTMM/mods': '.'}
PY_MODULES = ['openTMM/mods/boundary', 'openTMM/mods/layer']
EXT_MODULE = [Extension(name='openTMM.mods.fortran_utils', 
                        sources=['openTMM/mods/fortran_utils.f90'])]
DATA_FILES = [('openTMM/mods', ['openTMM/mods/fortran_utils.f90']),
              ('openTMM', ['./openTMMpreprint.pdf'])]
INSTALL_REQUIRES = ['scipy>=0.7.0', 'numpy>=1.3.0']
SETUP_REQUIRES = ['numpy>=1.3.0','setuptools>=0.6c9']


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Fortran',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Scientific/Engineering :: Atmospheric Science'
    ]


setup(name=NAME, 
      version=VERSION, 
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      classifiers=CLASSIFIERS,
      keywords='',
      author=AUTHOR,
      author_email=AUTHOR_EMAIL, 
      url=URL,
      license=LICENSE,
      platforms=PLATFORMS,
      packages=setuptools.find_packages(),
      package_dir=PACKAGE_DIR,
      py_modules=PY_MODULES,
      ext_modules=EXT_MODULE,
#      include_package_data = True,
#      package_data = PACKAGE_DATA,
      data_files=DATA_FILES,
      install_requires=INSTALL_REQUIRES,
      setup_requires=SETUP_REQUIRES, 
      zip_safe=False
      )
