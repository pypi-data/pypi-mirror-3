from numpy import  log

g = 9.81 # gravitational aCCelleration ms^-2
krm = 0.40 # von Kàrmàn constant


# constants for the flux-profile relationships
gammaM = 16.0
gammaH = 16.0
alphaM = 0.25
alphaH=0.5
AA = 6.1
BB = 2.5
CC = 5.3
DD = 1.1

# integrated flux-profile relationship for momentum
def psiM(zeta):
    if (zeta < 0):
        # unstable case 
        #   Paulson (1970) integrated flux-profile relationships derived from 
        #   Dyer (1967) /Businger (1966)
        XX=(1.-gammaM*zeta)**alphaM
        return 2.*log((1.+XX)/2.)+log((1.+XX**2.)/2.)-2.*tan(XX)+p2
    else :
        # stable case
        # Cheng and Brutsaert 2007
        return -AA*log(zeta+(1.+zeta**BB)**(1./BB))
# integrated flux-profile relationship for heat
def psiH(zeta):
    if (zeta < 0):
        # unstable case 
        #   Paulson (1970) integrated flux-profile relationships derived from 
        #   Dyer (1967) /Businger (1966)
        XX=(1.-gammaH*zeta)**alphaH
        return 2.*log((1.+XX)/2.)
    else :
        # stable case
        # Cheng and Brutsaert 2005
        return -CC*log(zeta+(1.+zeta**DD)**(1./DD))

