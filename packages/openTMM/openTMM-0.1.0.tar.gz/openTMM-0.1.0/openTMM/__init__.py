'''
Provides Boundary and Layer classes.  To access them use:
  import openTMM as tmm
  tmm.Boundary # Boundary class
  tmm.Layer # layer class

Boundary class -- Performs low-level calculations associated with the S-matrix method (TMM).
Layer class -- Performs high-level calculations such as computing the time-averaged 
               electric/magnetic energy density, the transverse component of the electric field,
               and the transmission and reflection coefficients.

For details, see Table 1 and 2 in Alex J. Yuffa, John A. Scales, Object-oriented electrodynamic 
S-matrix code with modern applications, preprint submitted to Journal of Computational Physics.
The preprint is distributed with the source code, see openTMMpreprint.pdf

If you want to access the modules where the two classes are implemented you must explicitly 
import them, i.e. :
  from openTMM.mods import boundary, layer
'''
__version__ = '0.1.0'
from mods.boundary import Boundary
from mods.layer import Layer
del mods

