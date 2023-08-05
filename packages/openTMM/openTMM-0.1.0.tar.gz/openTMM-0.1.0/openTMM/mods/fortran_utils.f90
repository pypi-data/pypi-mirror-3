SUBROUTINE get_chi(chi_plus, chi_minus, h, kx, w, num_of_regions)
  IMPLICIT NONE
  INTEGER, PARAMETER :: wp = KIND(0.0D0)
  ! Number of regions, num_of_regions, equals $p+1$, where $p$ is the
  ! label for a semi-infinite ambient medium.  [see Fig. 1 in the paper]
  ! In the code below, we keep the same indexing as in the paper.
  INTEGER, INTENT(IN) :: num_of_regions
  COMPLEX(wp), INTENT(IN) :: h(0:num_of_regions-1)
  COMPLEX(wp), INTENT(IN) :: kx(0:num_of_regions-1)
  COMPLEX(wp), INTENT(IN) :: w(0:num_of_regions-1)
  COMPLEX(wp), INTENT(OUT) :: chi_plus(0:num_of_regions-1)
  COMPLEX(wp), INTENT(OUT) :: chi_minus(0:num_of_regions-1)

  COMPLEX(wp) :: psi(0:num_of_regions-1), psi2(0:num_of_regions-1), s12(0:num_of_regions-1)
  COMPLEX(wp) :: tmp, denom
  COMPLEX(wp) :: J = (0.0_wp, 1.0_wp)
  INTEGER:: ell, p

  p = num_of_regions - 1

  ! fill in s12 [see (23a) in the paper]
  s12 = 0.0_wp
  psi = EXP(J*kx*h)
  psi2 = EXP(2.0_wp*J*kx*h)
  DO ell = 0, p-1
     tmp = w(ell) * (1.0_wp - s12(ell)) / (1.0_wp + s12(ell))
     s12(ell+1) = psi2(ell+1) * (w(ell+1) - tmp) / (w(ell+1) + tmp)
  END DO

  ! fill in chi_plus and set the incident $\chi$ to one, i.e., $\chi^+_p = 1$.
  chi_plus(p) = 1.0_wp
  DO ell = p-1, 0, -1
     ! [see (24a) in the paper]
     denom = w(ell+1) * (1.0_wp + s12(ell)) + w(ell) * (1.0_wp - s12(ell))
     chi_plus(ell) = 2.0_wp * w(ell+1) * psi(ell+1) * chi_plus(ell+1) / denom
     ! [see (24b) in the paper]
     chi_minus(ell+1) = s12(ell+1) * chi_plus(ell+1)
  END DO
  ! Set the reflected $\chi$ in a semi-infinite substrate to zero \chi^-_0 = 0$
  ! because there is no reflected wave in a semi-infinite substrate.
  chi_minus(0) = 0.0_wp 

END SUBROUTINE get_chi
!---------------------------------------------------------------------------------------------------
SUBROUTINE cmplx_sqrt(kx, kxSquared, num_of_regions)
  IMPLICIT NONE
  INTEGER, PARAMETER :: wp = KIND(0.0D0)
  ! Number of regions, num_of_regions, equals $p+1$, where $p$ is the
  ! label for the 'reflected' half-space.  [see Fig. 1 in the paper]
  ! In the code below, we keep the same indexing as in our paper.
  INTEGER, INTENT(IN) :: num_of_regions
  COMPLEX(wp), INTENT(IN) :: kxSquared(0:num_of_regions-1)
  COMPLEX(wp), INTENT(OUT) :: kx(0:num_of_regions-1)

  ! [see (8) in the paper]
  kx = SQRT(kxSquared)
  WHERE ( AIMAG(kx) < 0 ) kx = -kx
END SUBROUTINE cmplx_sqrt
!---------------------------------------------------------------------------------------------------
