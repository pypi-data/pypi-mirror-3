""" Utility functions and classes for SRP

Context : SRP
Module  : Frames
Version : 1.0.1
Author  : Stefano Covino
Date    : 01/10/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (28/09/2010) First version.
        : (01/10/2010) Sextractor command names.


"""

import os.path

import SRP

# SExtractor parameter sets for photometry

BasePath        = os.path.join(SRP.__path__[0],'SRPData','SExtractor') 

SexFName        = ("SRP.param", "SRP.conv", "SRP.nnw", "SRP.sex")

GenParSet       = ("SRPParamIn", "SRPConvIn", "SRPNnwIn", "SRPSexIn")

SRPSEXPARDICT   = {"LS-LASC":('SRPParamIn','SRPConvLSLASCIn','SRPNnwIn','SRPSexLSLASCIn'),
                    "REM-ROSS":('SRPParamIn','SRPConvIn','SRPNnwIn','SRPSexREMROSSIn'),
                    "REM-REMIR":('SRPParamIn','SRPConvIn','SRPNnwIn','SRPSexREMREMIRIn'),
                    "TNG-LRS":('SRPParamIn','SRPConvIn','SRPNnwIn','SRPSexTNGLRSIn')}


# SExtractor commands
SRPsex	       = "sex"
SRPsex_cyg     = "sex.exe"