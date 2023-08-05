import scipy as sp
from scipy import constants
from boundary import Boundary as bd
from warnings import warn

LHMwarning = '\n\nThe physical meaning of the returned values of the called function \nmay be NOT what you have expected because the multilayer stack contains \nat least one layer made of a left-handed material (LHM).  The LHM must be \naccompanied by frequency dispersion, see Sec. 6 in the paper.\n'

class Layer(bd):
    '''
    Layer class -- Performs high-level calculations such as computing the time-averaged 
                   electric/magnetic energy density, the transverse component of the electric field,
                   and the transmission and reflection coefficients.  The complete list of computed
                   quantities is given in Table 1 in the paper titled "Object-oriented 
                   electrodynamic S-matrix code with modern applications" by Alex J. Yuffa and 
                   John A. Scales.  The preprint of the paper is distributed with the source code, 
                   see openTMMpreprint.pdf
    '''
# Organization of the Layer class:
# The Layer class inherits the Boundary class and does NOT directly modify self.h, self.epsRel,
# self.muRel, self.pol, self.kx, self.w, self.chiPlus and self.chiMinus of the Boundary class.
# The public methods of the Layer class call the Boundary setChi method to compute self.kx, self.w,
# self.chiPlus and self.chiMinus and then calls an associated private method to convert them into
# a desired quantity.  For example, TRvsFreq calls Boundary.setChi first and then calls __T to 
# compute the transmission coefficient from the quantities computed by the Boundary.setChi method.

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
        bd.__init__(self, stack, patholMethod)
#---------------------------------------------------------------------------------------------------
    def __R(self):
        '''
        DESCRIPTION: 
        This function computes the reflection coefficient.

        INPUT:  None
        __R uses self.chiMinus to compute the reflection coefficient
        
        OUTPUT:
        R -- reflection coefficient (real value).
        '''
        # [see (37b) and (38b) in the paper]
        chiMinus_p = self.chiMinus[-1]
        R = chiMinus_p * chiMinus_p.conj()
        return R.real
#---------------------------------------------------------------------------------------------------
    def __T(self):
        '''
        DESCRIPTION: 
        This function computes the transmission coefficient.

        INPUT:  None
        __T uses self to compute the transmission coefficient.

        OUTPUT:
        T -- transmission coefficient (real value).
        '''
        chiPlus_0 = self.chiPlus[0]
        eps_0 = self.epsRel[0] * constants.epsilon_0
        eps_p = self.epsRel[-1] * constants.epsilon_0
        mu_0 = self.muRel[0] * constants.mu_0
        mu_p = self.muRel[-1] * constants.mu_0
        kx_0 = self.kx[0]
        kx_p = self.kx[-1].real
        
        if self.pol == 'perp':
            # [see (38a) in the paper]
            T = (mu_p / kx_p) * sp.real(kx_0.conj() / mu_0.conj()) * chiPlus_0 * chiPlus_0.conj()
        elif self.pol == 'parallel':
            # [see (37a) in the paper]
            T = kx_p * sp.real(eps_0.conj() * kx_0) / (eps_p * kx_0 * kx_0.conj()) * (
                chiPlus_0 * chiPlus_0.conj() )
        return T.real
#---------------------------------------------------------------------------------------------------
    def __field(self, xSample, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes transverse E-field; E_y if 'parallel' polarization or E_z if 'perp' polarization.
        [see (28) and (32) in the paper]

        INPUT:
        xSample - number of sample points per layer
        numAvgLayersOutside - How far (measured in average layer thickness) into a semi-infinite 
                              ambient medium and into a semi-infinite substrate should the field 
                              be computed.

        OUTPUT:
        x[ell,:] - discretization of $\ell^{th}$ layer; the distance is measured from the
                   top of the layer.
        gammaPlus[ell,:] - transverse component of the E-field associated with the wave propagating 
                           in the positive x-direction, where $\ell$ denotes the layer number,
                           i.e., gammaPlus[ell,:] is evaluated at x[ell,:]
        gammaMinus[ell,:] - transverse component of the E-field associated with the wave propagating
                            in the negative x-direction, where $\ell$ denotes the layer number,
                            i.e., gammaMinus[ell,:] is evaluated at x[ell,:]

        Case 1:  If numAvgLayersOutside = 0 then __field 
        RETURNS x, gammaPlus, gammaMinus
        x, gammaPlus and gammaMinus contain semi-infinite spaces with all values set to zero.
        The reason for doing so, is to keep indexing the same as in the paper, i.e.,
        x[0,:], gammaPlus[0,:], gammaMinus[0,:] refers to $0^{th}$ region (semi-infinite substrate)
        and x[-1,:], gammaPlus[-1,:], gammaMinus[-1,:] refers to region $p$ (semi-infinite ambient 
        medium)

        Case 2: If numAvgLayersOutside != 0 then __field 
        RETURNS x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside
        x, gammaPlus and gammaMinus are the same as in Case 1 and
        xOutside[0,:] - discretization of $0^{th}$ region (semi-infinite substrate); the
                        distance is measured from the top of the region, i.e., $1$--$0$ interface. 
        gammaPlusOutside[0,:] - transverse component of the E-field in the $0^{th}$ region associated
                                with the wave propagating in the positive x-direction, i.e.,
                                gammaPlusOutside[0,:] is evaluated at xOutside[0,:]
        gammaMinusOutside[0,:] - transverse component of the E-field in the $0^{th}$ region
                                 associated with the wave propagating in the negative x-direction,
                                 i.e., gammaMinusOutside[0,:] is evaluated at xOutside[0,:]
        xOutside[-1,:] - discretization of region $p$ (semi-infinite ambient medium); the distance
                         is measured from 'in-region' to the $p$--$p-1$ interface, i.e.,
                         xOutside[-1,-1] is the furthest point from the $p$--$p-1$ interface and
                         xOutside[-1,0] is the closest point to the $p$--$p-1$ interface
        gammaPlusOutside[-1,:] - transverse component of the E-field in region $p$ 
                                 associated with the wave propagating in the positive x-direction, 
                                 i.e., gammaPlusOutside[-1,:] is evaluated at xOutside[-1,:]
        gammaMinusOutside[-1,:] - transverse component of the E-field in region $p$
                                  associated with the wave propagating in the negative x-direction,
                                  i.e., gammaMinusOutside[-1,:] is evaluated at xOutside[-1,:]
        '''
        chiPlus = self.chiPlus[:,sp.newaxis]
        chiMinus = self.chiMinus[:,sp.newaxis]
        kx = self.kx[:,sp.newaxis]
        h = self.h[:,sp.newaxis]

        # In what follows, i denotes the layer number, i.e., i = 0,...,p and 
        # j refers to the discretization of layer's thickness, i.e., j = 0,...,xSample-1
        # x contains the discretization for each layer, i.e,
        # x[i,0] is the TOP of i-th layer, i.e., interface between i and i+1 layer.
        # x[i,-1] is the BOTTOM of i-th layer, i.e., interface between i and i-1 layer
        # and x[0,:] = 0, x[-1,:] = 0 (semi-infinite spaces are set to zero) 
        # For example, if p=4, h=3 for each layer, and xSample=3, then
        # x[0,:] = [0.0, 0.0, 0.0]
        # x[i,:] = [0.0, 1.0, 2.0], for i = 1,2,3 [see Fig. 1 in the paper]
        # x[-1,:] = [0.0, 0.0, 0.0]

        x = sp.zeros((self.h.size, xSample), float)
        for ell in xrange(1, self.h.size-1):
            x[ell] = sp.linspace(0.0, self.h[ell], xSample, endpoint=False)

        gammaPlus = chiPlus * sp.exp(1.0J * kx * x)
        gammaMinus = chiMinus * sp.exp(-1.0J * kx * x)
        gammaPlus[0], gammaPlus[-1] = 0.0, 0.0
        gammaMinus[0], gammaMinus[-1] = 0.0, 0.0

        if numAvgLayersOutside == 0:
            return x, gammaPlus, gammaMinus

        elif numAvgLayersOutside > 0:
            num = numAvgLayersOutside
            avgH = h.mean()
            numPts = xSample * num
            xOutside = sp.zeros((2,numPts), float)
            gammaPlusOutside = sp.zeros(xOutside.shape, complex)
            gammaMinusOutside = sp.zeros(xOutside.shape, complex)

            # Computing transverse E-field in a semi-infinite substrate, i.e., $\ell=0$.
            xOutside[0] = sp.linspace(0.0, num*avgH, numPts, endpoint=False)
            gammaPlusOutside[0] = chiPlus[0] * sp.exp(1.0J * kx[0] * xOutside[0])

            # Computing transverse E-field in a semi-infinite ambient medium, i.e., $\ell=p$
            xOutside[-1] = sp.linspace(-num*avgH, 0.0, numPts, endpoint=False)
            gammaPlusOutside[-1] = chiPlus[-1] * sp.exp(1.0J * kx[-1] * xOutside[-1])
            gammaMinusOutside[-1] = chiMinus[-1] * sp.exp(-1.0J * kx[-1] * xOutside[-1])

            return x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside
#---------------------------------------------------------------------------------------------------
    def __field2CoordSys(self, x, field, xOutside=None, fieldOutside=None):
        '''
        DESCRIPTION: 
        Converts field into a flat array as a function of distance as measured from the
        origin of the coordinate system set at the bottom of a semi-infinite ambient medium, i.e., 
        $p$--$p-1$ interface.
        Note: Here field denotes any quantity that is defined inside all layers,
              e.g., field could be $u^{\text{(e,m)}}(x)$, $Q^{\text{(e,m)}}(x)$, etc.
        
        INPUT:
        x[ell,:] - discretization of $\ell^{th}$ layer; the distance is measured from the
                   top of the layer.
        field[ell,:] - any field quantity evaluated at x[ell,:]
        WARNING:  The field values and discretization is dropped for a semi-infinite substrate and 
                  semi-infinite ambient medium ($\ell=0,p$) during OUTPUT computation, i.e.,
                  x[0,:], field[0,:], x[-1,:], field[-1,:]
                  must exist for INPUT but are NOT used in computation.

        INPUT (optional):
        xOutside[0,:] - discretization of $0^{th}$ region (semi-infinite substrate); the
                        distance is measured from the top of the region, i.e., 1--0 interface.
        xOutside[-1,:] - discretization of region $p$ (semi-infinite ambient medium); the distance
                         is measured from 'in-region' to the $p$--$p-1$ interface, i.e.,
                         xOutside[-1,-1] is the furthest point from the $p$--$p-1$ interface and
                         xOutside[-1,0] is the closest point to the $p$--$p-1$ interface 
        field[0,:] - any field quantity evaluated at xOutside[0,:]
        field[-1,:] - any field quantity evaluated at xOutside[-1,:]

        OUTPUT:
        x - flat array containing  discretization of distance as measured from the origin
            of the coordinate system (bottom of a semi-infinite ambient medium).
        field - flat array containing values of the field at x.
        '''
        # Make local copy of all input arguments, because they will be modified.
        x = x.copy()
        field = field.copy()
        insideCase = (xOutside is None) and (fieldOutside is None)
        if not insideCase:
            xOutside = xOutside.copy()
            fieldOutside = fieldOutside.copy()
        

        for ell in xrange(1, self.h.size-1):
            # Convert x[ell] to be measured from the origin of the coordinate system instead
            # of the top of each layer [see Fig. 1 in the paper]
            x[ell] = self.h[ell+1:-1].sum() + x[ell]
        
        # Because the origin of our coordinate system is set on the the $p$--$p-1$ interface
        # we must flip all columns in order to obtain a continuous x.  
        # For example, if p=4, h=3 for each layer, and xSample=4, then
        # BEFORE THE FLIP:
        # x[1,:] = [6.0, 7.0, 8.0]
        # x[2,:] = [3.0, 4.0, 5.0]
        # x[3,:] = [0.0, 1.0, 2.0]
        # AFTER THE FLIP:
        # x[1,:] = [0.0, 1.0, 2.0]
        # x[2,:] = [3.0, 4.0, 5.0]
        # x[3,:] = [6.0, 7.0, 8.0]
        # and then we can concatenate the rows to obtain a continuous x.    
        x = sp.flipud(x)
        field = sp.flipud(field)

        # Dropping semi-infinite ambient medium and semi-infinite substrate, i.e., $\ell=0,p$
        # because they contain all zero values, see function header.
        x = x[1:-1]
        field = field[1:-1]

        # Flatten all arrays and obtain a continuous x
        x = x.reshape(x.size)
        field = field.reshape(field.size)
        
        if not insideCase:
            # Computing distance in a semi-infinite substrate as measured 
            # from the origin of the coordinate system.
            xOutside[0] = self.h.sum() + xOutside[0]

            x = sp.concatenate((xOutside[-1], x, xOutside[0]))
            field = sp.concatenate((fieldOutside[-1], field, fieldOutside[0]))

        return x, field     
#---------------------------------------------------------------------------------------------------
    def field(self, fo, phi, xSample, pol, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes transverse E-field (E_y if 'parallel' polarization or E_z if 'perp' polarization)
        as a function of distance for a given frequency, angle of incidence, and polarization.
        [see (28) and (32) in the paper]

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        xSample - number of sample points per layer
                - scalar, integer
        pol - polarization it can be 'parallel' of 'perp' for perpendicular
            - string
        numAvgLayersOutside - How far (measured in average layer thickness) 
                              into a semi-infinite ambient medium and into a semi-infinite 
                              substrate should the field be computed.
                            - scalar, integer

        OUTPUT:
        x - discretization of distance as measured from the origin of the coordinate system,
            $p$--$p-1$ interface (bottom of semi-infinite ambient medium) [see Fig. 1 in the paper]
          - 1D array, float      
        gammaPlus - transverse component of the E-field associated with the wave propagating 
                    in the positive x-direction evaluated at x
                  - 1D array, complex
        gammaMinus - transverse component of the E-field associated with the wave propagating 
                     in the negative x-direction evaluated at x
                   - 1D array, complex

        REMARKS:
        The computed transverse E-field is normalized to $\chi^{+}_p$.  $\chi^{+}_p$ is the value
        of the incident transverse E-field at the $p$--$p-1$ interface. [see Fig. 1 in the paper]

        EXAMPLES:
        x, gammaPlus, gammaMinus = field(100.0, 30.0, 'perp')
        x, gammaPlus, gammaMinus = field(400,0, 45.0, 'parallel', 20)
        '''
        # Compute chiPlus & chiMinus in all layers at a given freq., incident angle, & polarization.
        phi = sp.deg2rad(phi)
        bd.setChi(self, fo, phi, pol)

        num = numAvgLayersOutside
        if num == 0:
            x, gammaPlus, gammaMinus = self.__field(xSample, 0)
            gammaPlus = self.__field2CoordSys(x, gammaPlus)[1]
            x, gammaMinus = self.__field2CoordSys(x, gammaMinus)
        elif num > 0:
            x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside = \
                self.__field(xSample, num)
            gammaPlus = self.__field2CoordSys(x, gammaPlus, xOutside, gammaPlusOutside)[1]
            x, gammaMinus = self.__field2CoordSys(x, gammaMinus, xOutside, gammaMinusOutside)

        return x, gammaPlus, gammaMinus
#---------------------------------------------------------------------------------------------------
    def __energy(self, fo, phi, gammaPlus, gammaMinus, case='inside'):
        '''
        DESCRIPTION:
        Computes electric and magnetic energy densities inside ($\ell=1,\ldots,p-1$) or outside 
        ($\ell=0,p$) of the multilayer stack.  [see (30), (31), (34) and (35) in the paper] 

        INPUT:
        fo - frequency in Hz (scalar, float)
        phi - angle of incidence in radians (scalar, float)

        If case = 'inside' then gammaPlus[ell,:] and gammaMinus[ell,:] have exactly the same
        meaning as in __field.

        If case = 'outside' then gammaPlus and gammaMinus have exactly the same meaning as 
        gammaPlusOutside and gammaMinusOutside in __field, respectively.

        OUTPUT:
        If case = 'inside' then  __energy returns
        u_e[ell,:] - electric energy density in $\ell^{th}$ layer at x[ell,:], where x[ell,:] is a 
                     discretization of $\ell^{th}$ layer, measured from the top of the layer.  
        u_m[ell,:] - magnetic energy density in $\ell^{th}$ layer at x[ell,:], where x[ell,:] is a 
                     discretization of $\ell^{th}$ layer, measured from the top of the layer.  
        Note: u_e and u_m contain semi-infinite spaces with all values set to zero.
        The reason for doing so, is to keep indexing the same as in the paper, i.e., 
        u_e[0,:], u_m[0,:] refers to $0^{th}$ region (semi-infinite substrate) and 
        u_e[-1,:], u_m[-1,:] refers to region $p$ (semi-infinite ambient medium).

        If case = 'outside' then __energy returns
        u_e[0,:] - electric energy density in a semi-infinite substrate ($\ell=0$) at x[0,:], where
                   x[0,:] is a discretization of the semi-infinite substrate.
        u_e[-1,:] - electric energy density in a semi-infinite ambient medium ($\ell=p$) at x[-1,:],
                    where x[-1,:] is a discretization of the semi-infinite ambient medium.
        u_m[0,:] - magnetic energy density in a semi-infinite substrate ($\ell=0$) at x[0,:], where
                   x[0,:] is a discretization of the semi-infinite substrate.
        u_m[-1,:] - magnetic energy density in a semi-infinite ambient medium ($\ell=p$) at x[-1,:],
                    where x[-1,:] is a discretization of the semi-infinite ambient medium. 

        WARNINGS:
        1.  This function should NOT be used if a multilayer stack contains any LHM layers.  
            [see Sec. 6 in the paper]
        2.  Both electric and magnetic energy densities are scaled to the total incident energy 
            density evaluated at the $p$--$p-1$ interface.
        '''
        # Compute epsilon, mu, kx, w
        if case == 'inside':
            eps = self.epsRel[:,sp.newaxis] * constants.epsilon_0
            mu = self.muRel[:,sp.newaxis] * constants.mu_0
            kx = self.kx[:,sp.newaxis]
            w = self.w[:,sp.newaxis]
        elif case == 'outside':
            eps = sp.zeros(2, complex)
            eps[0], eps[-1] = self.epsRel[0], self.epsRel[-1]
            eps = eps[:,sp.newaxis] * constants.epsilon_0

            mu = sp.zeros(2, complex)
            mu[0], mu[-1] = self.muRel[0], self.muRel[-1]
            mu = mu[:,sp.newaxis] * constants.mu_0
            
            kx = sp.zeros(2,complex)
            kx[0], kx[-1] = self.kx[0], self.kx[-1]
            kx = kx[:,sp.newaxis]

            w = sp.zeros(2, complex)
            w[0], w[-1] = self.w[0], self.w[-1]
            w = w[:,sp.newaxis]

        omega = 2.0 * sp.pi * fo
        kypSquared = eps[-1].real * mu[-1].real * omega**2 * sp.sin(phi)**2
        kRatioSquared  = kypSquared / sp.absolute(kx)**2

        # computation of the electric and magnetic energy densities
        u_e = sp.zeros(gammaPlus.shape, complex)
        u_m = sp.zeros(gammaPlus.shape, complex)
        if self.pol == 'parallel':
            # normalize energy density to the TOTAL incident energy density, hence the factor of 2
            norm = 2.0 * eps[-1].real/4.0 * 1.0/sp.cos(phi)**2

            # compute electric and magnetic energy densities [see (30) and (31) in the paper]
            u_e = eps.real/4.0 * (
                (1.0 + kRatioSquared) * (sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2)
                + 2.0 * (1.0 - kRatioSquared) * sp.real(gammaPlus * gammaMinus.conj()) )

            u_m = mu.real/4.0 * sp.absolute(w)**2 * (
                sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2 
                - 2.0 * sp.real(gammaPlus * gammaMinus.conj()) )
        elif self.pol == 'perp':
            # normalize energy density to the TOTAL incident energy density, hence the factor of 2
            norm = eps[-1].real/4.0

            # compute electric and magnetic energy densities [see (34) and (35) in the paper]
            u_e = eps.real/4.0 * ( sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2
                                   + 2.0 * sp.real(gammaPlus * gammaMinus.conj()) )

            u_m = mu.real/4.0 * sp.absolute(w)**2 * (
                (1.0 + kRatioSquared) * (sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2)
                - 2.0 * (1.0 - kRatioSquared) * sp.real(gammaPlus * gammaMinus.conj()) )

        return u_e.real/norm, u_m.real/norm
#---------------------------------------------------------------------------------------------------
    def energy(self, fo, phi, xSample, pol, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes electric and magnetic energy densities as a function of distance at a given 
        frequency, angle of incidence and polarization. [see (30), (31), (34) and (35) in the paper]

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        xSample - number of sample points per layer
                - scalar, integer
        pol - polarization it can be 'parallel' or 'perp' for perpendicular
            - string
        numAvgLayersOutside - How far (measured in average layer thickness) into a semi-infinite 
                              ambient medium and into a semi-infinite substrate should energy  
                              densities be computed.
                            - scalar, integer

        OUTPUT:
        x - discretization of distance as measured from the origin of the coordinate system,
            $p$--$p-1$ interface (bottom of semi-infinite ambient medium) [see Fig. 1 in the paper]
          - 1D array, float  
        u_e - contains values of the electric energy density at x
            - 1D array, float
        u_m - contains values of the magnetic energy density at x
            - 1D array, float

        WARNINGS:
        1.  This function should NOT be used if a multilayer stack contains any LHM layers.  
            [see Sec. 6 in the paper]
        2.  Both electric and magnetic energy densities are scaled to the total incident energy 
            density evaluated at the $p$--$p-1$ interface.

        EXAMPLES:
        x, u_e, u_m = energy(100.0, 30.0, 'perp')
        x, u_e, u_m = energy(400,0, 45.0, 'parallel', 20)
        '''
        phi = sp.deg2rad(phi)
        bd.setChi(self, fo, phi, pol)

        # issue a warning if LHM is detected
        LHM = sp.any(sp.signbit(self.epsRel.real) & sp.signbit(self.muRel.real))
        if LHM: 
            warn(LHMwarning)
            

        num = numAvgLayersOutside
        if num == 0:
            x, gammaPlus, gammaMinus = self.__field(xSample, 0)
            u_e, u_m = self.__energy(fo, phi, gammaPlus, gammaMinus, 'inside')
            
            # convert electric and magnetic energy densities to a function of distance
            u_e = self.__field2CoordSys(x, u_e)[1]
            x, u_m = self.__field2CoordSys(x, u_m)
        elif num > 0:
            x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside = \
                self.__field(xSample, num)
            u_eInside, u_mInside = self.__energy(fo, phi, gammaPlus, gammaMinus, 'inside')
            u_eOutside, u_mOutside = self.__energy(fo, phi, gammaPlusOutside, 
                                                          gammaMinusOutside, 'outside')

            # convert electric and magnetic energy densities to a function of distance
            u_e = self.__field2CoordSys(x, u_eInside, xOutside, u_eOutside)[1]
            x, u_m = self.__field2CoordSys(x, u_mInside, xOutside, u_mOutside)

        return x, u_e, u_m
#---------------------------------------------------------------------------------------------------
    def loss(self, fo, phi, xSample, pol, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes electric and magnetic loss densities as a function of distance at a given 
        frequency, angle of incidence, and polarization.  [see (25d) and (25e) in the paper]

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        xSample - number of sample points per layer
                - scalar, integer
        pol - polarization it can be 'parallel' or 'perp' for perpendicular
            - string
        numAvgLayersOutside - How far (measured in average layer thickness) into a semi-infinite 
                              ambient medium and into a semi-infinite substrate should electric and 
                              magnetic loss densities be computed.
                            - scalar, integer

        OUTPUT:
        x - discretization of distance as measured from the origin of the coordinate system,
            $p$--$p-1$ interface (bottom of semi-infinite ambient medium) [see Fig. 1 in the paper]
          - 1D array, float  
        Q_e - contains values of the electric loss density at x
            - 1D array, float
        Q_m - contains values of the magnetic loss density at x
            - 1D array, float

        WARNINGS:
        1.  This function should NOT be used if a multilayer stack contains any LHM layers.  
            [see Sec. 6 in the paper]
        2.  Both electric and magnetic loss densities are scaled to the total incident energy 
            density evaluated at the $p$--$p-1$ interface.

        EXAMPLES:
        x, Q_e, Q_m = loss(100.0, 30.0, 'perp')
        x, Q_e, Q_m = loss(400,0, 45.0, 'parallel', 20)
        '''
        phi = sp.deg2rad(phi)
        bd.setChi(self, fo, phi, pol)

        # issue a warning if LHM is detected
        LHM = sp.any(sp.signbit(self.epsRel.real) & sp.signbit(self.muRel.real))
        if LHM: 
            warn(LHMwarning)

        omega = 2.0 * sp.pi * fo
        u_e2Q_e = 2.0 * self.epsRel.imag * omega / self.epsRel.real
        u_m2Q_m = 2.0 * self.muRel.imag * omega / self.muRel.real
            
        num = numAvgLayersOutside
        if num == 0:
            x, gammaPlus, gammaMinus = self.__field(xSample, 0)
            u_e, u_m = self.__energy(fo, phi, gammaPlus, gammaMinus, 'inside')
            Q_e = u_e2Q_e[:,sp.newaxis] * u_e
            Q_m = u_m2Q_m[:,sp.newaxis] * u_m 
            
            # convert electric and magnetic loss densities to a function of distance
            Q_e = self.__field2CoordSys(x, Q_e)[1]
            x, Q_m = self.__field2CoordSys(x, Q_m)
        elif num > 0:
            x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside = \
                self.__field(xSample, num)
            u_eInside, u_mInside = self.__energy(fo, phi, gammaPlus, gammaMinus, 'inside')
            u_eOutside, u_mOutside = self.__energy(fo, phi, gammaPlusOutside, 
                                                          gammaMinusOutside, 'outside')

            Q_eOutside = sp.zeros(u_eOutside.shape, float)
            Q_mOutside = sp.zeros(u_mOutside.shape, float)
            Q_eOutside[0], Q_eOutside[-1] = u_e2Q_e[0] * u_eOutside[0], u_e2Q_e[-1] * u_eOutside[-1]
            Q_mOutside[0], Q_mOutside[-1] = u_m2Q_m[0] * u_mOutside[0], u_m2Q_m[-1] * u_mOutside[-1]
            Q_eInside = u_e2Q_e[:,sp.newaxis] * u_eInside
            Q_mInside = u_m2Q_m[:,sp.newaxis] * u_mInside

            # convert electric and magnetic loss densities to a function of distance
            Q_e = self.__field2CoordSys(x, Q_eInside, xOutside, Q_eOutside)[1]
            x, Q_m = self.__field2CoordSys(x, Q_mInside, xOutside, Q_mOutside)

        return x, Q_e, Q_m
#---------------------------------------------------------------------------------------------------
    def __divS(self, fo, phi, gammaPlus, gammaMinus, case='inside'):
        '''
        DESCRIPTION:
        Computes divergence of the time-average complex Poynting vector inside ($\ell=1,\ldots,p-1$)
        or outside ($\ell=0,p$) of the multilayer stack.  [see Sec. 6 in the paper]

        INPUT:
        fo - frequency in Hz (scalar, float)
        phi - angle of incidence radians (scalar, float)

        If case = 'inside' then gammaPlus[ell,:] and gammaMinus[ell,:] have exactly the same
        meaning as in __field.

        If case = 'outside' then gammaPlus and gammaMinus have exactly the same meaning as 
        gammaPlusOutside and gammaMinusOutside in __field, respectively.

        OUTPUT:
        If case = 'inside' then  __divS returns
        divS[ell,:] - divergence of the time-average complex Poynting vector in $\ell^{th}$ layer 
                      at x[ell,:], where x[ell,:] is a discretization of $\ell^{th}$ layer, 
                      measured from the top of the layer.  
        Note: divS contains semi-infinite spaces with all values set to zero.
              The reason for doing so, is to keep indexing the same as in the paper, i.e.,
              divS[0,:] refers to $0^{th}$ region (semi-infinite substrate) and divS[-1,:] refers to
              region $p$ (semi-infinite ambient medium).

        If case = 'outside' then __divS returns
        divS[0,:] - divergence of the time-averaged complex Poynting vector in a semi-infinite 
                    substrate ($\ell=0$) at x[0,:], where x[0,:] is a discretization of the 
                    semi-infinite substrate.
        divS[-1,:] - divergence of the time-averaged complex Poynting vector in a semi-infinite 
                     ambient medium ($\ell=p$) at x[-1,:], where x[-1,:] is a discretization of the 
                     semi-infinite ambient medium.

        WARNINGS:
        1.  This function should NOT be used if a multilayer stack contains any LHM layers.  
            [see Sec. 6 in the paper]
        2.  $div \cdot \mathbf{S}$ is scaled to the total incident energy density evaluated
            at the $p$--$p-1$ interface.
        '''
        # compute epsilon, mu and kx
        if case == 'inside':
            eps = self.epsRel[:,sp.newaxis] * constants.epsilon_0
            mu = self.muRel[:,sp.newaxis] * constants.mu_0
            kx = self.kx[:,sp.newaxis]
        elif case == 'outside':
            eps = sp.zeros(2, complex)
            eps[0], eps[-1] = self.epsRel[0], self.epsRel[-1]
            eps = eps[:,sp.newaxis] * constants.epsilon_0

            mu = sp.zeros(2, complex)
            mu[0], mu[-1] = self.muRel[0], self.muRel[-1]
            mu = mu[:,sp.newaxis] * constants.mu_0
            
            kx = sp.zeros(2,complex)
            kx[0], kx[-1] = self.kx[0], self.kx[-1]
            kx = kx[:,sp.newaxis]

        omega = 2.0 * sp.pi * fo

        # computation of the divS
        divS = sp.zeros(gammaPlus.shape, complex)
        if self.pol == 'parallel':
            # normalize divS to the total incident energy density, hence the factor of 2.
            norm = 2.0 * eps[-1].real/4.0 * 1.0/sp.cos(phi)**2

            divS = -eps.conj() * omega / kx.conj() * (
                kx.imag * (sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2)
                + 2.0J * kx.real * sp.real(gammaPlus * gammaMinus.conj()) )

        elif self.pol == 'perp':
            # normalize divS to the total incident energy density, hence the factor of 2.
            norm = eps[-1].real/4.0

            divS = -kx.conj() / (mu.conj() * omega) * (
                kx.imag * (sp.absolute(gammaPlus)**2 + sp.absolute(gammaMinus)**2)
                + 2.0J * kx.real * sp.real(gammaPlus * gammaMinus.conj()) )            

        return divS/norm
#---------------------------------------------------------------------------------------------------
    def divPoynting(self, fo, phi, xSample, pol, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes divergence of the time-averaged complex Poynting vector as a function of distance 
        at a given frequency, angle of incidence, and polarization. [see Sec. 6 in the paper]

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        xSample - number of sample points per layer
                - scalar, integer
        pol - polarization it can be 'parallel' or 'perp' for perpendicular
            - string
        numAvgLayersOutside - How far (measured in average layer thickness) 
                              into a semi-infinite ambient medium and into a semi-infinite 
                              substrate should the $div \cdot \mathbf{S}$ be computed.
                            - scalar, integer

        OUTPUT:
        x - discretization of distance as measured from the origin of the coordinate system,
            $p$--$p-1$ interface (bottom of semi-infinite ambient medium) [see Fig. 1 in the paper]
          - 1D array, float
        divS - contains values of the divergence of the time-average complex Poynting vector at x
             - 1D array, float

        WARNINGS:
        1.  This function should NOT be used if a multilayer stack contains any LHM layers.  
            [see Sec. 6 in the paper]
        2.  $div \cdot \mathbf{S}$ is scaled to the total incident energy density evaluated
            at the $p$--$p-1$ interface.

        EXAMPLES:
        x, divS = divPoynting(100.0, 30.0, 'perp')
        x, divS = divPoynting(400,0, 45.0, 'parallel', 20)
        '''
        phi = sp.deg2rad(phi)
        bd.setChi(self, fo, phi, pol)

        # issue a warning if LHM is detected
        LHM = sp.any(sp.signbit(self.epsRel.real) & sp.signbit(self.muRel.real))
        if LHM: 
            warn(LHMwarning)

        num = numAvgLayersOutside
        if num == 0:
            x, gammaPlus, gammaMinus = self.__field(xSample, 0)
            divS = self.__divS(fo, phi, gammaPlus, gammaMinus, 'inside')
            
            # convert divergence of the Poynting vector as a function of distance
            x, divS = self.__field2CoordSys(x, divS)
        elif num > 0:
            x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside = \
                self.__field(xSample, num)
            divS_Inside = self.__divS(fo, phi, gammaPlus, gammaMinus, 'inside')
            divS_Outside = self.__divS(fo, phi, gammaPlusOutside, gammaMinusOutside, 'outside')


            # convert divergence as a function of distance
            x, divS = self.__field2CoordSys(x, divS_Inside, xOutside, divS_Outside)

        return x, divS
#---------------------------------------------------------------------------------------------------
    def FIM(self, fo, phi, pol):
        '''
        DESCRIPTION: 
        Computes the "Fundamental Invariant of Multilayers" (FIM) at each layer interface
        at a given frequency, angle of incidence and polarization. [see (27) in the paper]

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        pol - polarization it can be 'parallel' or 'perp' for perpendicular
            - string

        OUTPUT:
        FIMbottom[ell-1] - FIM at the bottom of the $\ell^{th}$ layer (interface 
                           separating $\ell$--$\ell-1$ layers) for $\ell = 1,\ldots,p$.
                           Notice the shift in the argument of FIMbottom.  This is necessary because
                           the $0^{th}$ region is a semi-infinite substrate but SciPy's array must
                           start at the zero index.
                         - 1D array, complex
        FIMtop[ell] - FIM at the top of of the $\ell^{th}$ layer (interface 
                      separating $\ell$--$\ell+1$ layers) for $\ell = 0,\ldots,p-1$.
                    - 1D array, complex

        EXAMPLES:
        FIMbottom, FIMtop = FIM(100.0, 30.0, 'perp')
        FIMbottom, FIMtop = FIM(110.0, 10.0, 'parallel')
        '''
        bd.setChi(self, fo, sp.deg2rad(phi), pol)

        # FIM at the bottom of $\ell^{th}$ region for $\ell=1,\ldots,p$. [see Fig. 1 in the paper]
        psi = sp.exp(1.0J * self.kx * self.h)
        FIMbottom = self.w[1:] * ((psi[1:]*self.chiPlus[1:])**2 - (self.chiMinus[1:]/psi[1:])**2) 

        # FIM at the top of $\ell^{th}$ region for $\ell=0,\ldots,p-1$. [see Fig. 1 in the paper]
        FIMtop = self.w[0:-1] * (self.chiPlus[0:-1]**2 - self.chiMinus[0:-1]**2)

        return FIMbottom, FIMtop
#---------------------------------------------------------------------------------------------------
    def FIMvsDist(self, fo, phi, xSample, pol, numAvgLayersOutside=0):
        '''
        DESCRIPTION:
        Computes "Fundamental Invariant of Multilayers" (FIM) as a function of distance at
        a given frequency, angle of incidence and polarization.

        INPUT:
        fo - frequency in Hz
           - scalar, float
        phi - angle of incidence in degrees
            - scalar, float
        xSample - number of sample points per layer
                - scalar, integer
        pol - polarization it can be 'parallel' of 'perp' for perpendicular
            - string
        numAvgLayersOutside - How far (measured in average layer thickness) into a semi-infinite 
                              ambient medium and into a semi-infinite substrate should the FIM be 
                              computed.
                            - scalar, integer

        OUTPUT:
        x - discretization of distance as measured from the origin of the coordinate system,
            $p$--$p-1$ interface (bottom of semi-infinite ambient medium) [see Fig. 1 in the paper]
          - 1D array, float
        FIM - value of the "Fundamental Invariant of Multilayers" at x
             - 1D array, complex

        EXAMPLES:
        x, FIM = FIMvsDist(100.0, 30.0, 'perp')
        x, FIM = FIMvsDist(400,0, 45.0, 'parallel', 20)
        '''
        phi = sp.deg2rad(phi)
        bd.setChi(self, fo, phi, pol)

        num = numAvgLayersOutside
        # compute $\gamma^{\pm}(x)$ in each layer and half-spaces if num > 0 
        # [see (28) and (32) in the paper]
        if num == 0:
            x, gammaPlus, gammaMinus = self.__field(xSample, 0)
        elif num > 0:
            x, gammaPlus, gammaMinus, xOutside, gammaPlusOutside, gammaMinusOutside = \
                self.__field(xSample, num)

        # compute FIM inside $\ell = 1,..,p-1$ regions [see the right-hand side of (27) in the paper]
        FIM = self.w[:,sp.newaxis] * (gammaPlus**2 - gammaMinus**2)

        # convert FIM to the coordinate system, i.e., FIM as a function of distance
        if num == 0:
            x, FIM = self.__field2CoordSys(x, FIM)
        elif num > 0:
            # compute FIM in a semi-infinite substrate ($\ell=0$) and in a semi-infinite ambient
            # medium ($\ell=p).
            wOutside = sp.zeros((2,1), complex)
            wOutside[0,0], wOutside[1,0] = self.w[0], self.w[-1]
            FIMoutside = wOutside * (gammaPlusOutside**2 - gammaMinusOutside**2)

            x, FIM = self.__field2CoordSys(x, FIM, xOutside, FIMoutside)
                
        return x, FIM
#---------------------------------------------------------------------------------------------------
    def TRvsFreq(self, fmin, fmax, fSample, phi, pol):
        '''
        DESCRIPTION:
        Computes transmission and reflection coefficients as a function of frequency at a given
        angle of incidence, and polarization, i.e., $T(f)$ and $R(f)$. [see Sec. 7 in the paper]
        
        INPUT: 
        fmin - minimal frequency in Hertz
             - scalar, float
        fmax - maximum frequency in Hertz
             - scalar, float
        fSample - number of sample points in [fmin,fmax] interval
                - scalar, integer
        phi - angle of incidence in degrees
            - scalar, float
        pol - polarization, 'parallel' or 'perp' for perpendicular
            - string

        OUTPUT: 
        f - frequency in Hertz
          - 1D array, float
        T - transmission coefficient at f, i.e., $T(f)$
          - 1D array, float
        R - reflection coefficient at f, i.e., $R(f)$
          - 1D array, float

        EXAMPLES: 
        Computes T and R in [1Hz,100Hz] frequency interval with 1000 sample points
        at an angle of incidence of 20 degrees with parallel polarization.
        f, T, R = TRvsFreq(1.0, 100.0, 1000, 20.0, 'parallel')
        '''
        phi = sp.deg2rad(phi)
        f = sp.linspace(fmin, fmax, fSample)
        T = sp.zeros(f.size, float)
        R = sp.zeros(f.size, float)
        for ix in xrange(f.size):
            bd.setChi(self, f[ix], phi, pol)
            T[ix] = self.__T()
            R[ix] = self.__R()

        return f, T, R
#---------------------------------------------------------------------------------------------------
    def TRvsAngle(self, phiMin, phiMax, phiSample, f, pol):
        '''
        DESCRIPTION:
        Computes transmission and reflection coefficients as a function of angle of incidence
        at a given frequency, and polarization, i.e., $T(\phi)$ and $R(\phi)$, where $\phi$ is
        in degrees.  [see Sec. 7 in the paper]

        INPUT: 
        phiMin - minimal angle of incidence in degrees
               - scalar, float
        phiMax - maximum angle of incidence in degrees
               - scalar, float
        phiSample - number of sample points in [phiMin,phiMax] interval
                  - scalar, integer
        f - frequency in Hertz
          - scalar, float
        pol - polarization, 'parallel' or 'perp' for perpendicular
            - string

        OUTPUT: 
        phi - angle of incidence in degrees
            - 1D array, float
        T - transmission coefficient at phi, i.e., $T(\phi)$
          - 1D array, float
        R - reflection coefficient at phi, i.e., $R(\phi)$
          - 1D array, float

        EXAMPLES:
        Computes T and R in [10 degrees, 30 degrees] incidence angle interval with 100 sample points
        at a frequency of 150.0 Hz with perpendicular polarization.
        phi, T, R = TRvsAngle(10.0, 30.0, 100, 150.0, 'perp')
        '''
        phi = sp.deg2rad( sp.linspace(phiMin, phiMax, phiSample) )
        T = sp.zeros(phi.size, float)
        R = sp.zeros(phi.size, float)
        for ix in xrange(phi.size):
            bd.setChi(self, f, phi[ix], pol)
            T[ix] = self.__T()
            R[ix] = self.__R()

        return sp.rad2deg(phi), T, R
#---------------------------------------------------------------------------------------------------
    def TRvsFreqAndAngle(self, fmin, fmax, fSample, phiMin, phiMax, phiSample, pol):
        '''
        DESCRIPTION:
        Computes transmission and reflection coefficients as a function of frequency and angle of
        incidence at a given polarization, i.e, $T(f,\phi)$ and $T(f,\phi)$.
        [see Sec. 7 in the paper]
        
        INPUT: 
        fmin - minimal frequency in Hertz
             - scalar, float
        fmax - maximum frequency in Hertz
             - scalar, float
        fSample - number of sample points in [fmin,fmax] interval
                - scalar, integer
        phiMin - minimal angle of incidence in degrees
               - scalar, float
        phiMax - maximum angle of incidence in degrees
               - scalar, float
        phiSample - number of sample points in [phiMin,phiMax] interval
                  - scalar, integer
        pol - polarization, 'parallel' or 'perp' for perpendicular
            - string

        OUTPUT: 
        fMat - frequency in Hertz; fMat[i,:] = sp.linspace(fmin, fmax, fSample)
             - 2D array, float
        phiMat - angle of incidence in degrees; phiMat[:,i] = sp.linspace(phiMin, phiMax, phiSample)
               - 2D array, float
        T - transmission coefficient at fMat and phiMat, i.e., $T(f,\phi)$
          - 2D array, float
        R - reflection coefficient at fMat and phiMat, i.e., $R(f,\phi)$
          - 2D array, float

        EXAMPLES: 
        Computes T and R in [1Hz, 100Hz] frequency interval with 1000 sample points
        and [10 degrees, 40 degrees] angle of incidence interval with 200 sample points  
        (parallel polarization).
        f, phi, T, R = TRvsFreqAndAngle(1.0, 100.0, 1000, 10.0, 40.0, 200, 'parallel')
        '''
        # Discretize frequency and angle of incidence
        fVec = sp.linspace(fmin, fmax, fSample)
        phiVec = sp.deg2rad( sp.linspace(phiMin, phiMax, phiSample) )

        # Each row of fMat contains fVec and each column of phiMat contains phiVec
        fMat, phiMat = sp.meshgrid(fVec, phiVec)
        Nrows, Ncols = fMat.shape

        # Each row of T/R contains T/R for all frequencies at a fixed angle on incidence.
        # Each column of T/R contains T/R for all angles of incidence at fixed frequency.
        T = sp.zeros(fMat.shape, float)
        R = sp.zeros(fMat.shape, float)
        for row in xrange(Nrows):
            for col in xrange(Ncols):
                bd.setChi(self, fMat[row,col], phiMat[row,col], pol)
                R[row,col] = self.__R()
                T[row,col] = self.__T()

        return fMat, sp.rad2deg(phiMat), T, R
#---------------------------------------------------------------------------------------------------
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# MAY BE INCLUDE PHASE CALCULATIONS IN THE NEXT RELEASE % 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#     def phaseVSfreq(self, fmin, fmax, fSample, phi, pol, wrapped=False):
#         '''
#         DESCRIPTION:  
#         Computes phase of the transverse component (E_y if 'parallel' polarization or
#         E_z if 'perp' polarization) of the transmitted/reflected E-field as a function of frequency
#         at a given angle of incidence, and polarization.

#         INPUT:
#         fmin - minimal frequency in Hertz
#              - scalar, float
#         fmax - maximum frequency in Hertz
#              - scalar, float
#         fSample - number of sample points in [fmin,fmax] interval
#                 - scalar, integer
#         phi - angle of incidence in degrees
#             - scalar, float
#         pol - polarization, 'parallel' or 'perp' for perpendicular
#             - string
#         wrapped - (optional) If set to True then wrapped phase is returned.  
#                   If set to False (default) then unwrapped phase is returned.
#                 - Boolean

#         OUTPUT:
#         f - frequency in Hertz
#           - 1D array, float
#         Tphase - transmitted E-field phase in degrees at f
#                - 1D array, float
#         Rphase - reflected E-field phase in degrees at f
#                - 1D array, float

#         REMARKS:
#         The computed phase is relative to the phase of the incident transverse E-field at the
#         interface between $p$--$p-1$ layer.  In other words, the computed phase is the phase of
#         $\frac{\chi^{\pm}_0}{\chi^{+}_p}$.

#         WARNING:
#         Only the phase of the transverse E-field is computed.  It's not even clear what one
#         means by phase at non-zero angle of incidence with parallel polarization because E-field
#         has two components.

#         EXAMPLES:
#         f, Tphase, Rphase = phaseVSfreq(10.0, 100.0, 1000, 30, 'perp')
#         f, Tphase, Rphase = phaseVSfreq(20.0, 200.0, 2000, 60, 'parallel', True)
#         '''
#         phi = sp.deg2rad(phi)
#         f = sp.linspace(fmin, fmax, fSample)

#         # Compute wrapped phase for each frequency
#         Tphase = sp.zeros(f.shape, float)
#         Rphase = sp.zeros(f.shape, float)
#         for ix in xrange(f.size):
#             bd.setChi(self, f[ix], phi, pol)
#             Tphase[ix] = sp.angle(self.chiPlus[0])
#             Rphase[ix] = sp.angle(self.chiMinus[-1])

#         # Unwrap phase
#         if not wrapped:
#             Tphase = sp.unwrap(Tphase)
#             Rphase = sp.unwrap(Rphase)

#         return f, sp.rad2deg(Tphase), sp.rad2deg(Rphase)
# #---------------------------------------------------------------------------------------------------
#     def phaseVSangle(self, phiMin, phiMax, phiSample, f, pol, wrapped=False):
#         '''
#         DESCRIPTION:  
#         Computes the phase of the transverse component (E_y if 'parallel' polarization or
#         E_z if 'perp' polarization) of the transmitted/reflected E-field as a function of 
#         angle of incidence at a given frequency, and polarization.

#         INPUT:
#         phiMin - minimal angle of incidence in degrees
#                - scalar, float
#         phiMax - maximum angle of incidence in degrees
#                - scalar, float
#         phiSample - number of sample points in [phiMin,phiMax] interval
#                   - scalar, integer
#         f - frequency in Hertz
#           - scalar, float
#         pol - polarization, 'parallel' or 'perp' for perpendicular
#             - string
#         wrapped - (optional) If set to True then wrapped phase is returned.  
#                   If set to False (default) then unwrapped phase is returned.
#                 - Boolean

#         OUTPUT:
#         phi - angle of incidence in degrees
#             - 1D array, float
#         Tphase - transmitted E-field phase in degrees at phi
#                - 1D array, float
#         Rphase - reflected E-field phase in degrees at phi
#                - 1D array, float

#         REMARKS:
#         The computed phase is relative to the phase of the incident transverse E-field at the
#         interface between $p$--$p-1$ layer.  In other words, the computed phase is the phase of 
#         $\frac{\chi^{\pm}_0}{\chi^{+}_p}$.

#         WARNING:
#         Only the phase of the transverse E-field is computed.  It's not even clear what one
#         means by phase at non-zero angle of incidence with parallel polarization because E-field
#         has two components.

#         EXAMPLES:
#         phi, Tphase, Rphase = phaseVSfreq(10.0, 100.0, 1000, 30, 'perp')
#         phi, Tphase, Rphase = phaseVSfreq(20.0, 200.0, 2000, 60, 'parallel', True)
#         '''
#         phi = sp.deg2rad( sp.linspace(phiMin, phiMax, phiSample) )
        
#         # Compute wrapped phase for each angle of incidence
#         Tphase = sp.zeros(phi.shape, float)
#         Rphase = sp.zeros(phi.shape, float)
#         for ix in xrange(phi.size):
#             bd.setChi(self, f, phi[ix], pol)
#             Tphase[ix] = sp.angle(self.chiPlus[0])
#             Rphase[ix] = sp.angle(self.chiMinus[-1])

#         # Unwrap phase
#         if not wrapped:
#             Tphase = sp.unwrap(Tphase)
#             Rphase = sp.unwrap(Rphase)

#         return sp.rad2deg(phi), sp.rad2deg(Tphase), sp.rad2deg(Rphase)
# #---------------------------------------------------------------------------------------------------
