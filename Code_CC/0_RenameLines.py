# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import glob
import re
import numpy as np
import pandas as pd
from skimage import io, exposure


import UtilityFunctions as ufun


#%% Renaming files for easier handling

DirLines = 'D:/CollectiveMigrationData/MaskLines/'
allSpeeds = os.listdir(DirLines)[1:]

for i in range(len(allSpeeds)):
    DirSpeed = DirLines+'/'+allSpeeds
    names = os.listdir(DirSpeed)
    ufun.renameFiles(DirSpeed, 0)


#%%
DirLines = 'D:/CollectiveMigrationData/MaskLines'
speed = '0.31um_hr'

maskArray = ufun.getLineMask(DirLines, speed)



