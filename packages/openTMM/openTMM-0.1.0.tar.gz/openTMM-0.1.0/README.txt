This is openTMM-0.1.0 README.txt file.
 
LEGAL
-------------------------------------------------------------------------------
This library is free software; you can redistribute it and/or
modify it under the terms of The MIT License, 
http://www.opensource.org/licenses/mit-license.php

Copyright (c) 2010, Alex J. Yuffa <ayuffa@gmail.com>
-------------------------------------------------------------------------------


OVERVIEW
-------------------------------------------------------------------------------
openTMM is an object-oriented electrodynamic S-matrix (transfer matrix) code 
with modern applications.

Electromagnetic wave propagation through planar stratified media (multilayer 
stack); the three-dimensional space is divided into layers.  The interfaces 
separating the layers are assumed to be perfectly planar and the layers are 
assumed to be isotropic and homogeneous, with a complex permittivity and 
permeability.  Moreover, the layers may be composed of a left-handed material 
(negative refractive material) and/or a right-handed material.  The 
implementation is suitable for the study of modern applications, e.g., Anderson 
localization of light and sub-wavelength imaging.

For more details see our preprint, openTMMpreprint.pdf, which is distributed 
with the source code.
-------------------------------------------------------------------------------


REQUIREMENTS
-------------------------------------------------------------------------------
openTMM needs at least:
* python-2.5
* setuptools-0.6c9
* numpy-1.3.0
* scipy-0.7.0

If you are going to compile openTMM from source you will also need
a Fortran 90/95 compiler and C compiler, e.g., GNU Fortran 95 compiler and
standard UNIX-style compiler.
-------------------------------------------------------------------------------


DOWNLOAD
-------------------------------------------------------------------------------
You may download the latest stable release from 
  http://pypi.python.org/pypi/openTMM

The latest development snapshot is available from
  http://mesoscopic.mines.edu/mediawiki/index.php/Free_Python_codes
Be aware that the latest development version is NOT guaranteed to be fully
functional.
-------------------------------------------------------------------------------


INSTALLATION
-------------------------------------------------------------------------------
See INSTALL.txt for detailed description.  For your convenience here is
a quick installation guide.

  Linux/Unix/MacOS X Users (with root privileges):
    $ python setup.py install
  or
    $ python setup.py config config_fc --fcompiler=gnu95 install
  
  Linux/Unix/MacOS X Users (without root privileges):
    $ python setup.py install --user
  or 
    $ python setup.py config config_fc --fcompiler=gnu95 install --user

  Windows Users:        
  Download the binary openTMM-0.1.0.win32-py2.7.exe and double click
  it to install openTMM.
-------------------------------------------------------------------------------


BASIC USAGE
-------------------------------------------------------------------------------
 $ python
 >>> import scipy as sp
 >>> import openTMM as tmm
 >>> mm = 1.0 * 10**-3
 >>> GHz = 1.0 * 10**9
 >>> stackDict = {}
 >>> stackDict['epsilonRelative'] = sp.array([1,2,3], float)
 >>> stackDict['muRelative'] = sp.array([1.2, 1.0, 1.5 + 0.01J], complex)
 >>> stackDict['height'] = sp.array([0.01, 0.2, 0.03], float) * mm
 >>> stack = tmm.Layer(stackDict)
 >>> x, u_e, u_m = stack.energy(fo=100.0*GHz, phi=8.0, xSample=100, pol='perp') 

More examples will be posted on
http://mesoscopic.mines.edu/mediawiki/index.php/Free_Python_codes

Our preprint, openTMMpreprint.pdf, which is distributed with the source code,
also contains some basic information about the usage and organization of
the code.
-------------------------------------------------------------------------------


NOTE
----
For best viewing of the source code, set your editors' column width to 100, 
the usual default value is 80.
