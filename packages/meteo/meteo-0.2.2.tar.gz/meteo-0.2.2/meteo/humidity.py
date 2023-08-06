#!/usr/bin/python
# Filename: radiation.py

from numpy import log10

# Description:
# conversions between different humidity quantities

Mw=18.0160 # molecular weight of water
Md=28.9660 # molecular weight of dry air

#saturation pressure
def esat(T):
    ''' get sateration pressure (units [Pa]) for a given air temperature (units [K])'''
    from numpy import log10
    TK = 273.15
    e1 = 101325.0
    logTTK = log10(T/TK)
    esat =  e1*10**(10.79586*(1-TK/T)-5.02808*logTTK+ 1.50474*1e-4*(1.-10**(-8.29692*(T/TK-1)))+ 0.42873*1e-3*(10**(4.76955*(1-TK/T))-1)-2.2195983) 
    return esat

# conversion relative humidity to mixing ratio
def rh2mixr(RH,p,T):
    es = esat(T)
    return Mw/Md*RH/100.*es/(p-RH/100.*es)*1000.

# conversion mixing ratio to specific humidity (always kg/kg)
def mixr2sh(W):
    '''conversion from mixing ratio (units [kg/kg]) to specific humidity (units also [kg/kg])
    '''
    return W/(1.+W)
def sh2mixr(qv):
    '''conversion from specific humidity (units [kg/kg]) to mixing ratio (units also [kg/kg])
    '''
    return qv/(1.-qv)
def ea2mixr(P,ea):
    '''conversion from dry air and vapour pressure (units [Pa]) to mixing ratio (units [kg/kg]) 
    '''
    return 0.622*ea/(P-ea)
def mixr2ea(P,mixr):
    '''conversion from dry air pressure (units [Pa]) and mixing ratio (units [kg/kg] to vapour pressure (units [Pa])
    '''
    return P*mixr/(0.622+ea)

