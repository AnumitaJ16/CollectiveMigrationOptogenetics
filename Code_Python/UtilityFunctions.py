# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 21:26:21 2022

@author: anumi
"""


import os
import re
import sys

import numpy as np
import pandas as pd
import scipy.stats as st

import matplotlib.pyplot as plt
from skimage import io, exposure

import GraphicStyles as gs
import LinesPaths as lp
sys.path.append(lp.DirRepoPython)

dateFormatExcel = re.compile(r'[1-2]\d{1}/\d{2}/(?:19|20)\d{2}') # matches X#/##/YY## where X in {1, 2} and YY in {19, 20}
dateFormatExcel2 = re.compile(r'[1-2]\d-\d{2}-(?:19|20)\d{2}') # matches X#-##-YY## where X in {1, 2} and YY in {19, 20}
dateFormatOk = re.compile(r'\d{2}-\d{2}-\d{2}')

#%%
def renameFiles(DirPath, startingNo = 0):
    """

    :param DirPath: Path of the diretory with the files you want to rename
    :type DirPath: string
    :return: Renames files with numbers to be easily callable in Python for manipulation later. Usually .tif files.

    """
    files = os.listdir(DirPath)
    i = startingNo
    j = 0
    for file in files:
        if 'Copy' in file:
            if i < 10:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '000'+str(i)+'.tif'))
                i+=1
            elif i >= 10 and i < 100:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '00'+str(i)+'.tif'))
                i+=1
            elif i >= 100:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '0'+str(i)+'.tif'))
                i+=1
        else:
            file = str(j)+'.tif'
            if i < 10:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '000'+str(i)+'.tif'))
                i+=1
                j+=1
            elif i >= 10 and i < 100:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '00'+str(i)+'.tif'))
                i+=1
                j+=1
            elif i >= 100:
                os.rename(os.path.join(DirPath,file), os.path.join(DirPath, '0'+str(i)+'.tif'))
                i+=1
                j+=1

def getLineMask(DirLines, speed):
    dirPath = DirLines+'/'+speed
    file_spec = '*.tif'
    load_pattern = os.path.join(dirPath, file_spec)
    ic = io.imread_collection(load_pattern)
    imgArray = np.uint8(io.concatenate_images(ic))
    print('Images loaded succesffuly. Creating mask...')
    lineMask = np.mean(imgArray, axis = 2).T
    imgArray = lineMask.copy()
    
    imgArray.max()
    imgArray.min()
    imgArray_scaled = exposure.rescale_intensity(imgArray)
    imgArray_scaled.max()
    imgArray_scaled.min()
    scaledArray = np.round(imgArray_scaled)
    plt.imshow(scaledArray)
    return scaledArray

def getExperimentalConditions(DirExp, save = False, suffix = '_AJ'):
    """
    Import the table with all the conditions in a clean way.
    It is a tedious function to read because it's doing a boring job:
    Converting strings into numbers when possible; 
    Converting commas into dots to correct for the French decimal notation; 
    Converting semicolon separated values into lists when needed; 
    \n
    NEW FEATURE: Thanks to "engine='python'" in pd.read_csv() the separator can now be detected automatically !
    """
    
    #### 0. Import the table
    if suffix == '':
        experimentalDataFile = 'ExperimentalConditions.csv'
    else:
        experimentalDataFile = 'ExperimentalConditions' + suffix + '.csv'
        
    experimentalDataFilePath = os.path.join(DirExp, experimentalDataFile)
    expDf = pd.read_csv(experimentalDataFilePath, sep=None, header=0, engine='python')
    # print(gs.BLUE + 'Importing Experimental Conditions' + gs.NORMAL)
    print(gs.BLUE + 'Experimental Conditions Table has ' + str(expDf.shape[0]) + ' lines and ' + str(expDf.shape[1]) + ' columns' + gs.NORMAL)
    #### 1. Clean the table
    
    #### 1.1 Remove useless columns
    for c in expDf.columns:
        if 'Unnamed' in c:
            expDf = expDf.drop([c], axis=1)
        if '.1' in c:
            expDf = expDf.drop([c], axis=1)
    expDf = expDf.convert_dtypes()

    #### 1.2 Convert commas into dots
    listTextColumns = []
    for col in expDf.columns:
        try:
            if expDf[col].dtype == 'string':
                listTextColumns.append(col)
        except:
            pass
    expDf[listTextColumns] = expDf[listTextColumns].apply(lambda x: x.str.replace(',','.'))

    #### 1.3 Format 'scale'
    expDf['scale pixel per um'] = expDf['scale pixel per um'].astype(float)
    

    #### 1.8 Format 'date'
    dateExemple = expDf.loc[expDf.index[1],'date']
    if re.match(dateFormatExcel, dateExemple):
        print(gs.ORANGE + 'dates : format corrected' + gs.NORMAL)
        expDf.loc[:,'date'] = expDf.loc[:,'date'].apply(lambda x: x.split('/')[0] + '-' + x.split('/')[1] + '-' + x.split('/')[2][2:])        
    elif re.match(dateFormatExcel2, dateExemple):
        print(gs.ORANGE + 'dates : format corrected' + gs.NORMAL)
        expDf.loc[:,'date'] = expDf.loc[:,'date'].apply(lambda x: x.split('-')[0] + '-' + x.split('-')[1] + '-' + x.split('-')[2][2:])  
        
    #### 1.9 Format projected lines fields
    try:
        # expDf['lines speed'] = expDf['lines speed'].astype(np.float)
        expDf['static duration'] = expDf['static duration'].astype(np.float)
    except:
        pass

    #### 2. Save the table, if required
    if save:
        saveName = 'ExperimentalConditions' + suffix + '.csv'
        savePath = os.path.join(DirExp, saveName)
        expDf.to_csv(savePath, sep=';', index = False)
        

    #### 3. Generate additionnal field that won't be saved
    
    #### 3.1 Make 'manipID'
    expDf['manipID'] = expDf['date'] + '_' + expDf['position'].astype(str)

    #### 4. END
    return(expDf)

def addStat_df(ax, data, box_pairs, param, cond, test = 'Mann-Whitney', percentHeight = 95):
    refHeight = np.percentile(data[param].values, percentHeight)
    currentHeight = refHeight
    scale = ax.get_yscale()
    xTicks = ax.get_xticklabels()
    dictXTicks = {xTicks[i].get_text() : xTicks[i].get_position()[0] for i in range(len(xTicks))}
    for bp in box_pairs:
        c1 = data[data[cond] == bp[0]][param] #.values
        c2 = data[data[cond] == bp[1]][param] #.values
        if test == 'Mann-Whitney' or test == 'Wilcox_2s' or test == 'Wilcox_greater' or test == 'Wilcox_less' or test == 't-test':
            if test=='Mann-Whitney':
                statistic, pval = st.mannwhitneyu(c1,c2)
            elif test=='Wilcox_2s':
                statistic, pval = st.wilcoxon(c1,c2, alternative = 'two-sided')
            elif test=='Wilcox_greater':
                statistic, pval = st.wilcoxon(c1,c2, alternative = 'greater')
            elif test=='Wilcox_less':
                statistic, pval = st.wilcoxon(c1,c2, alternative = 'less')
            elif test=='t-test':
                statistic, pval = st.ttest_ind(c1,c2)
            text = 'ns'
            if pval == np.nan:
                text = 'nan'
            if pval < 0.05 and pval > 0.01:
                text = '*'
            elif pval < 0.01 and pval > 0.001:
                text = '**'
            elif pval < 0.001 and pval < 0.001:
                text = '***'
            elif pval < 0.0001:
                text = '****'
            
            # print('Pval')
            # print(pval)
            ax.plot([bp[0], bp[1]], [currentHeight, currentHeight], 'k-', lw = 1)
            XposText = (dictXTicks[bp[0]]+dictXTicks[bp[1]])/2
            
            if scale == 'log':
                power = 0.01* (text=='ns') + 0.000 * (text!='ns')
                YposText = currentHeight*(refHeight**power)
            else:
                factor = 0.03 * (text=='ns') + 0.000 * (text!='ns')
                YposText = currentHeight + factor*refHeight
            
            # if XposText == np.nan or YposText == np.nan:
            #     XposText = 0
            #     YposText = 0
                
            ax.text(XposText, YposText, text, ha = 'center', color = 'k')
    #         if text=='ns':
    #             ax.text(posText, currentHeight + 0.025*refHeight, text, ha = 'center')
    #         else:
    #             ax.text(posText, currentHeight, text, ha = 'center')
            if scale == 'log':
                currentHeight = currentHeight*(refHeight**0.05)
            else:
                currentHeight =  currentHeight + 0.15*refHeight
        # ax.set_ylim([ax.get_ylim()[0], currentHeight])

        if test == 'pairwise':
            ratio = (c2/c1)
            stdError = np.nanstd(ratio)/np.sqrt(np.size(c1))
            confInt = np.nanmean(ratio) - 1.96 * stdError
            print(stdError)
            print(confInt)
            return confInt
        
def date2expt(date):
    dateSplit = date.split('-')
    expt = '20'+dateSplit[0]+dateSplit[1]+dateSplit[2]
    return expt