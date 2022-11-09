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

import UtilityFunctions as ufun


#%% Renaming files for easier handling


DirLines = 'D:/Anumita/CollectiveMigrationData/MaskLines'
allSpeeds = os.listdir(DirLines)[2:]

for i in range(len(allSpeeds)):
    DirSpeed = DirLines+'/'+allSpeeds[i]
    names = os.listdir(DirSpeed)
    ufun.renameFiles(DirSpeed, 0)


