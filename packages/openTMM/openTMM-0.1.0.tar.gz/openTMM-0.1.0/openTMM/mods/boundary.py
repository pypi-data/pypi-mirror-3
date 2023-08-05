import scipy as sp
from scipy import constants
from fortran_utils import get_chi, cmplx_sqrt
from warnings import warn

epsComplexWarning = '\n\nImaginary part of $\epsilon_p$ was ignored because $\epsilon_p$ must be real, see Section 3 of the paper.\n'
muComplexWarning = '\n\nImaginary part of $\mu_p$ was ignored because $\mu_p$ must be real, see Section 3 of the paper.\n'

class Boundary:
    '''
    Boundary class -- Performs low-level calculations associated with the S-matrix method. 
                      This class is meant to be a base class (superclass in the Python 
                      lexicon) that will be inherited by the derived classes (subclasses in the 
                      Python lexicon).  This class computes and sets the following quantities:

                      self.h - thickness of each layer
                      self.epsRel - relative permittivity
                      self.muRel - relative permeability
                      self.pol - polarization state
                      self.kx - x-component of the wavevector, $k_{x,\ell}$
                      self.w - scaled version (polarization dependent) of $k_{x,\ell}$
                      self.chiPlus - transverse component of the electric field evaluated
                                     on the interface, $\chi^+_{\ell} / \chi^+_p$
                      self.chiMinus - transverse component of the electric field evaluated 
                                      on the interface, $\chi^-_{\ell} / \chi^+_p$

                      See Table 2 in the paper titled "Object-oriented electrodynamic S-matrix code 
                      with modern applications" by Alex J. Yuffa and John A. Scales.  The preprint 
                      of the paper is distributed with the source code, see openTMMpreprint.pdf

                      USAGE:  After creating a Boundary object via __init__ e.g.,
                              >>> bdStack = openTMM.Boundary(stackDict)
                              h, epsRel and muRel are set and ready to be used, i.e,
                              >>> bdStack.xxx 
                              where xxx is h, epsRe or muRel.  The main method of the class is
                              setChi.  After calling setChi, i.e.,
                              >>> bdStack.setChi(frequency, angle_of_incidence, pol)
                              pol, kx, w, chiPlus and chiMinus are set/computed and may be used via
                              >>> bdStack.xxx
                              where xxx is pol, kx, w, chiPlus, chiMinus.
    '''

# For best viewing, set your editors' column width to 100, the usual default value is 80.
#---------------------------------------------------------------------------------------------------
    def __init__(self, stack, patholMethod='makeComplex'):
        '''
        INPUT Type: 
        stack -- dictionary
          stack['height'] -- 1D, ndarray, float, e.g., sp.array([1,2,3], float)
          stack['epsilonRelative'] -- 1D, ndarray, float/complex, e.g.,  
                                      sp.array([1+1J,3,4J], complex)
          stack['muRelative'] -- 1D, ndarray, float/complex
          stack['hostMedia']['epsilonRelative'] -- 1D, ndarray, float/complex
          stack['hostMedia']['muRelative'] -- 1D, ndarray float/complex

        patholMethod -- string

        INPUT DESCRIPTION:  
        stack - mandatory [see Fig. 1 in the paper]
          Let arg = stack['xxx'], where 'xxx' = 'height' or 'epsilonRelative' or 'muRelative'.
          arg[0] refers to the 1st layer, $\ell=1$
                 NOTE: $\ell=1$ layer is next to a semi-infinite substrate.
          arg[1] refers to the 2nd layer, $\ell=2$
          arg[ell] refers to the $\ell^{\text{th}}$ layer, $\ell < p$, where region $p$ is a 
                   semi-infinite ambient medium.

        stack['hostMedia'] - optional [see Fig. 1 in the paper]
          Let arg = stack['hostMedia']['xxx'], where 'xxx' = 'epsilonRelative' or 'muRelative'.  
          If stack['hostMedia'] is not given then the host media is assumed to be free space.
          arg[0] refers to a semi-infinite substrate, $\ell=0$
          arg[1] refers to a semi-infinite ambient medium, $\ell=p$

        patholMethod = 'makeComplex' (default) or 'keepReal' [see Sec. 3.2 in the paper]
          If 'makeComplex' then small absorption is added to the zero absorption layers.
          If 'keepReal' then no absorption is added to the zero absorption layers and
          the code may produce erroneous results at or very near the critical angles.
          Note that patholMethod only affects the pathological cases, i.e., 
          when $ \left\{ \epsilon_{\ell}, \mu_{\ell} \right\} \in \mathbb{R} $ and
          $ \epsilon_{\ell} \mu_{\ell} \omega^2 \geq k_{y,p}^2 $ [see Sec. 3.1 in the paper]
        '''
        self.h = None
        self.__setHeight(stack)
        self.epsRel = None
        self.__setEpsilonRel(stack)
        self.muRel = None
        self.__setMuRel(stack)


        # Zero absorption layers cause all of the pathological cases and must be identified
        # and dealt with according to the patholMethod (pathological method) selected.
        # [see Sec. 3.2 in the paper]
        self._ixIdealLHM = None
        self._ixIdealRHM = None
        self.__idZeroAbsorptionLayers()
        self._patholMethod = patholMethod
        if patholMethod == 'makeComplex':
            self.__fixZeroAbsorptionLayers()

        # The following are set by __setEMparams during $\chi^{\pm}_{\ell}$ computation.
        self.pol = None
        self.kx = None
        self.w = None

        # The following are set by setChi.
        self.chiPlus = None
        self.chiMinus = None
#---------------------------------------------------------------------------------------------------
    def __setHeight(self, stack):
        '''
        DESCRIPTION: 
        This function stores the height of each layer into self.h, i.e., 
        self.h[ell] for $\ell=0,\ldots,p$.

        INPUT:
        stack as described in __init__
        
        OUTPUT: Nothing is returned but self.h is stored.
        Let h = stack['height'] then self.h contains the height of each layer.  
        The height of a semi-infinite substrate and semi-infinite ambient medium are set to zero, 
        i.e.,
        self.h[0] = 0.0 -- semi-infinite substrate, $\ell=0$ 
        self.h[1] -- height of the 1st layer, $\ell=1$
        self.h[2] -- height of the 2nd layer, $\ell=2$
        self.h[h.size+1] -- height of the $\ell=p-1$ layer 
        self.h[h.size+2] = 0.0 -- semi-infinite ambient medium, $\ell=p$
        Thus, self.h[ell] is defined for $\ell = 0, \ldots, p$.
        [see Fig. 1 as well as Sections 4.0.1 and 4.0.2 in the paper]
        '''
        h = stack['height']
        self.h = sp.zeros(h.size+2, float)
        self.h[1:h.size+1] = h
#---------------------------------------------------------------------------------------------------
    def __setEpsilonRel(self, stack):
        '''
        DESCRIPTION: 
        This function stores relative permittivity of each layer into self.epsRel, i.e.,
        self.epsRel[ell] for $\ell=0,\ldots,p$.

        INPUT:
        stack as described in __init__

        OUTPUT: Nothing is returned but self.epsRel is stored.
        Let epsRel = stack['epsilonRelative'] then self.epsRel contains the relative permittivity
        of each layer, i.e.,
        self.epsRel[0] -- relative permittivity of the semi-infinite substrate, $\ell=0$.
        self.epsRel[1] -- relative permittivity of the 1st layer, $\ell=1$.
        self.epsRel[epsRel.size+1] -- relative permittivity of the $\ell=p-1$ layer.
        self.epsRel[epsRel.size+2] -- relative permittivity of the semi-infinite ambient medium, 
                                      $\ell=p$.
        [see Fig. 1 and Sec. 3 in the paper]
        '''
        epsRel = stack['epsilonRelative']
        self.epsRel = sp.ones(epsRel.size+2, complex)
        self.epsRel[1:epsRel.size+1] = epsRel

        if stack.has_key('hostMedia'):
            self.epsRel[0] = stack['hostMedia']['epsilonRelative'][0]
            self.epsRel[-1] = stack['hostMedia']['epsilonRelative'][1].real
            if sp.iscomplex(stack['hostMedia']['epsilonRelative'][1]):
                warn(epsComplexWarning)
#---------------------------------------------------------------------------------------------------
    def __setMuRel(self, stack):
        '''
        DESCRIPTION: 
        This function stores relative permeability of each layer into self.muRel, i.e., 
        self.muRel[ell] for $\ell=0,\ldots,p$.

        INPUT:
        stack as described in __init__

        OUTPUT: Nothing is returned but self.muRel is stored.
        Let muRel = stack['muRelative'] then self.muRel contains the relative permeability
        of each layer, i.e.,
        self.muRel[0] -- relative permeability of the semi-infinite substrate, $\ell=0$.
        self.muRel[1] -- relative permeability of the 1st layer, $\ell=1$.
        self.muRel[muRel.size+1] -- relative permeability of the $\ell=p-1$ layer.
        self.muRel[muRel.size+2] -- relative permeability of the semi-infinite ambient medium, 
                                    $\ell=p$.
        [see Fig. 1 and Sec. 3 in the paper]
        '''
        muRel = stack['muRelative']
        self.muRel = sp.ones(muRel.size+2, complex)
        self.muRel[1:muRel.size+1] = muRel

        if stack.has_key('hostMedia'):
            self.muRel[0] = stack['hostMedia']['muRelative'][0]
            self.muRel[-1] = stack['hostMedia']['muRelative'][1].real
            if sp.iscomplex(stack['hostMedia']['muRelative'][1]):
                warn(muComplexWarning)
#---------------------------------------------------------------------------------------------------
    def __idZeroAbsorptionLayers(self):
        '''
        DESCRIPTION:
        This function uses self.epsRel and self.muRel to identify zero absorption layers.
        The identification of zero absorption layers is needed because zero absorption layers
        cause all pathological cases.  [see Sections 3.1 and 3.2 in the paper]

        INPUT: None.  The function uses self.epsRel and self.muRel

        OUTPUT: Nothing is returned but self._ixIdealRHM and self._ixIdealLHM are stored.
        self._ixIdealRHM[ell] is set to True if $\ell^{th}$ layer is made of a right-handed material
        with zero absorption and self._ixIdealRHM[ell] is set to False otherwise, $\ell=0,\ldots,p$.
        self._ixIdealLHM[ell] is set to True if $\ell^{th}$ layer is made of a left-handed material
        with zero absorption and self._ixIdealLHM[ell] is set to False otherwise, $\ell=0,\ldots,p$.
        '''
        epsRel = self.epsRel
        muRel = self.muRel

        # Recall that according to the IEEE 754 standards, zero is represented exactly,
        # e.g., see http://steve.hollasch.net/cgindex/coding/ieeefloat.html or
        # http://en.wikipedia.org/wiki/Floating_point
        # Thus, hard comparison should be fine, assuming that the relative permittivity and 
        # relative permeability used to initialize the Boundary class did NOT come from some 
        # some previous calculation.
        ixZeroAbsorption = sp.isreal(epsRel) & sp.isreal(muRel)
        self._ixIdealRHM = ixZeroAbsorption & ~sp.signbit(epsRel.real) & ~sp.signbit(muRel.real)
        self._ixIdealLHM = ixZeroAbsorption & sp.signbit(epsRel.real) & sp.signbit(muRel.real)
#---------------------------------------------------------------------------------------------------
    def __fixZeroAbsorptionLayers(self):
        '''
        DESCRIPTION:
        This function adds a small imaginary part to absorption-free layers identified by
        self._ixIdealRHM and self._ixIdealLHM.  Note $\ell=p$ layer is NOT modified because
        this is a semi-infinite ambient medium which MUST be absorption free.  
        [see Sec. 3 in the paper]

        INPUT: None. The function uses self.epsRel, self.muRel

        OUTPUT: Nothing is returned but self.epsRel and self.muRel are modified for layers
                where self._ixIdealRHM or self._ixIdealLHM is True
        '''
        ixZeroAbsorption = self._ixIdealRHM | self._ixIdealLHM

        small = 10**-100
        self.epsRel[ixZeroAbsorption] += small * 1.0J
        self.muRel[ixZeroAbsorption] += small * 1.0J
        # $\ell=p$ layer must be kept with zero absorption, because the wave 
        # is incident from region $p$ (semi-infinite ambient medium). [see Sec. 3 in the paper] 
        self.epsRel[-1] = self.epsRel[-1].real
        self.muRel[-1] = self.muRel[-1].real
#---------------------------------------------------------------------------------------------------
    def __setEMparams(self, f, phi, pol):
        '''
        DESCRIPTION:
        This function computes and stores $k_{x,\ell=0,\ldots,p}$ and $w_{\ell=0,\ldots,p}$ 
        into self.  Polarization state is also stored into self, i.e., self.pol
        [see Section 3 and 4 in the paper]

        INPUT:
        f - frequency in Hertz
          - float, scalar
        phi - angle of incidence in radians
            - float, scalar
        pol - polarization, 'parallel' if the electric field is parallel to the $xy$ plane or 'perp'
              if the electric field is perpendicular to the $xy$-plane. [see Fig. 1 in the paper]
            - string
        
        OUTPUT: Nothing is returned but self.kx, self.w and self.pol are stored.
        self.pol - polarization state, 'parallel' or 'perp'
        self.kx[ell] - x-component of the wavevector, i.e, $k_{x,\ell}$ for $\ell=0,\ldots,p$. 
        self.w[ell] - scaled version of self.kx[ell], scaling depends on polarization state.
                      [see (15) and (19) in the paper]
        '''
        self.pol = pol
        epsRel = self.epsRel
        muRel = self.muRel
        omega = 2.0 * sp.pi * f

        # Compute scaled $k_{x, \ell = 0,\ldots,p}$ and choose physically appropriate root, i.e.,
        # imaginary part of $k_{x, \ell = 0,\ldots,p} > 0$, [see (8) in the paper]
        kypSquared = epsRel[-1].real * muRel[-1].real * sp.sin(phi)**2
        kx = cmplx_sqrt(epsRel * muRel - kypSquared)

        # handle pathological cases with zero absorption according to 'keepReal' scheme.
        # [see second scheme in Sec. 3.2 of the paper]
        if self._patholMethod == 'keepReal':
            ixRealKx = sp.isreal(kx)

            ixLHM = self._ixIdealLHM & ixRealKx
            kx[ixLHM] = -sp.absolute(kx[ixLHM].real)

            ixRHM = self._ixIdealRHM & ixRealKx
            kx[ixRHM] = sp.absolute(kx[ixRHM].real)

        # Fix $k_{x,p}$ if region $p$ is made of a left-handed material because region $p$ 
        # is always absorption-free.  Moreover, note that __fixZeroAbsorptionLayers 
        # did NOT add a small imaginary part to self.epsRel[p] and self.muRel[p]
        if self._patholMethod == 'makeComplex' and self._ixIdealLHM[-1]:
            kx[-1] = -sp.absolute(kx[-1].real)

        # compute scaled version of $w_{\ell=0,\ldots,p}$ parameter [see (15) and (19) in the paper]
        if self.pol == 'parallel':
            w = epsRel / kx
        elif self.pol == 'perp':
            w = -kx / muRel

        # Un-scale kx and w (SI unit system)
        self.kx = kx * omega / constants.c
        self.w = w * constants.epsilon_0 * constants.c
#---------------------------------------------------------------------------------------------------
    def setChi(self, f, phi, pol):
        '''
        DESCRIPTION:
        This function computes and stores $\chi^+_{\ell=0,\ldots,p}$ and $\chi^-_{\ell=0,\ldots,p}$ 
        into self.  Note: $\chi^+_{\ell=p}$ is set to one, thus, $\chi^{\pm}_{\ell=0,\ldots,p}$ are
        really $\frac{\chi^{\pm}_{\ell=0,\ldots,p}}{\chi^+_p}$. $\chi^-_{\ell=0}$ is set to zero
        because there is no reflected wave in the $0^{th}$ region (semi-infinite substrate).
        [see Fig. 1 and (13), (18) in the paper]

        INPUT:
        f - frequency in Hertz
          - float, scalar
        phi - angle of incidence in radians
            - float, scalar
        pol - polarization, 'parallel' if the electric field is parallel to the $xy$ plane or 'perp'
              if the electric field is perpendicular to the $xy$-plane. [see Fig.1 in the paper]
            - string
        
        OUTPUT: Nothing is returned but self.chiPlus and self.chiMinus are stored.
        self.chiPlus[ell] - $\chi^+_{\ell}$ for $\ell=0,\ldots,p$
        self.chiMinus[ell] - $chi^-_{\ell}$ for $\ell=0,\ldots,p$
        '''
        # Set all E&M parameters needed to compute $\chi^{\pm}_{\ell=0,\ldots,p}
        self.__setEMparams(f, phi, pol)

        self.chiPlus, self.chiMinus = get_chi(self.h, self.kx, self.w)
#---------------------------------------------------------------------------------------------------
