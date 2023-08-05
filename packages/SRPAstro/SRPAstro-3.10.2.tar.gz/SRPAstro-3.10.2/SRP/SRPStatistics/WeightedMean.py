""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 21/05/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input is a list of (x,sigmax)

History : (21/05/2010) First version.

"""


import math


def WeightedMean(lst):
    num = 0.0
    den = 0.0
    for i in lst:
        num = num + i[0]*i[1]**-2
        den = den + i[1]**-2
    wa = num/den
    sum = 0.0
    for i in lst:
        sum = sum + (wa - i[0])**2
    ws = math.sqrt(sum/(len(lst)-1))
    we = ws/math.sqrt(len(lst))
    rchis = 0.0
    for i in lst:
        rchis = rchis + ((i[0]-wa)/i[1])**2
    rchis = rchis/(len(lst)-1)
    return wa,ws,we,rchis
