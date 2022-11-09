# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:43:04 2022

@author: Joseph Vermeil & Anumita Jawahar
"""

import os
import sys
import ctypes
from datetime import date

# %% 1. Paths

COMPUTERNAME = os.environ['COMPUTERNAME']

# 1.1 Init main directories
    
if COMPUTERNAME == 'DESKTOP-K9KOJR2':
    suffix = '_AJ'
    DirRepo = "C://Users//anumi//OneDrive//Desktop//CollectiveMigrationOptogenetics"
    DirData = "D:/Anumita/CollectiveMigrationData"
    #### TBC !!!
    DirCloud = ""# + suffix

# TBC for Celine
elif COMPUTERNAME =='':
    suffix = '_CC'
    DirRepo = ""
    DirData = ""
    DirCloud = ""# + suffix
    DirTempPlots = ''
    
# 1.2 Init sub directories

DirRepoPython = os.path.join(DirRepo, "Code_Python")
DirRepoPythonUser = os.path.join(DirRepoPython, "Code" + suffix)
DirRepoExp = os.path.join(DirRepo, "Data_Experimental" + suffix)

DirDataRaw = os.path.join(DirData, "Raw")

DirDataAnalysis = os.path.join(DirData, "Data_Analysis")
DirDataTimeseries = os.path.join(DirData, "Data_Timeseries")

DirDataFig = os.path.join(DirData, "Figures")
DirDataFigToday = os.path.join(DirDataFig, "Historique", str(date.today()))

# 1.3 Add python directory to path

sys.path.append(DirRepoPython)

