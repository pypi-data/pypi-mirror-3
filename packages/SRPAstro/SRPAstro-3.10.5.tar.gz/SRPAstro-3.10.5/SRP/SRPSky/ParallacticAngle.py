""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 09/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : site and object should be valid pyephem objects.

History : (09/02/2012) First version.

"""

import ephem
import math
from SRP.SRPSky.HourAngle import HourAngle


def ParallacticAngle (object,site):
#    f1 = math.cos(site.lat)
#    f2 = math.sin(math.radians(HourAngle(math.degrees(float(object.a_ra)),site)))
#    f3 = math.sin(math.radians(90.0)-object.alt)
#    if f3 == 0:
#        return 0.0
#    else:
#        fact = f1*f2/f3
#        if -1.0 <= fact <= 1.0:
#            return math.degrees(math.asin(fact))
#        else:
#            f2 = math.sin(object.az)
#            f3 = math.cos(object.a_dec)
#            fact = f1*f2/f3
#            return math.degrees(math.asin(fact))
    #
    f1 = math.sin(site.lat)
    f2 = math.sin(object.a_dec)
    f3 = math.cos(object.a_dec)
    f4 = math.sin(object.alt)
    f5 = math.cos(object.alt)
    if f3 == 0.0 or f5 == 0.0:
        return 0.0
    else:
        fact = (f1-f2*f4)/(f3*f5)
    if fact < -1:
        fact = -1.0
    elif fact > 1.0:
        fact = 1.0
    else:
        return math.degrees(math.acos(fact))
