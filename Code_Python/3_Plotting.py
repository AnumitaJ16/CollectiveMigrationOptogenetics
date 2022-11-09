# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 14:11:56 2022

@author: anumi
"""

import os

import numpy as np
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import UtilityFunctions as ufun

#Plotting conditions

#MAP = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
MAP = 'winter_r'

xtickfont = 20
ytickfont = 20

xlabelfont = 20
ylabelfont = 20
titlefont = 30

figsize = (15,10)

#%%

dates = '21-07-27'
pos = 3


# Import expperimental files
expt = ufun.date2expt(dates)
dirExp = "C:/Users/anumi/OneDrive/Desktop/CollectiveMigrationOptogenetics/Data_Experimental_AJ"
expDf = ufun.getExperimentalConditions(dirExp)
expDf = expDf[expDf['manipID'] == dates+'_'+str(pos)]

lineSpeed = expDf['line speed'].values[0]

dirAnalysis = "D:/Anumita/CollectiveMigrationData/Data_Analysis/"+expt
dirFig = "D:/Anumita/CollectiveMigrationData/Figures/Historique/"+str(date.today())

try:
    os.mkdir(dirAnalysis)
except:
    pass

try:
    os.mkdir(dirFig)
except:
    pass


##Trapping region for the static phase (first 12 hrs)

dirData = 'D:/Anumita/CollectiveMigrationData/Data_Timeseries/'
tracks = pd.read_csv(dirData+expt+'/Position'+str(pos)+'_tracking_results.csv')

tracks['xvelocity'] = [np.nan]*len(tracks)
tracks['yvelocity'] = [np.nan]*len(tracks)


staticDur = expDf['static duration']

if np.sum(staticDur.notna()) == 0:
    staticDur = 0
    
timeRes = expDf['time resolution']
scale = expDf['scale pixel per um']
staticFrame = int(staticDur/timeRes)
staticPhase = tracks[tracks['frame'] < staticFrame]
movingPhase = tracks[tracks['frame'] > staticFrame]


allCells = np.unique(tracks['particle'])
xvelocity = []
xdisp = []
ydisp = []
yvelocity = []

for cell in allCells:
    df = movingPhase[movingPhase['particle'] == cell]

    timeInt = float(timeRes)/60
    scale = float(scale)
    x_disp = (np.roll(df['x'], -1) - df['x'])/scale
    y_disp = (np.roll(df['y'], -1) - df['y'])/scale
    
    x_vel = x_disp/timeInt
    y_vel = y_disp/timeInt
    
    xvelocity.extend(x_vel.values)
    yvelocity.extend(y_vel.values)
    xdisp.extend(x_disp.values)
    ydisp.extend(y_disp.values)
    
movingPhase['xvelocity'] = xvelocity
movingPhase['yvelocity'] = yvelocity
movingPhase['xdisp'] = xdisp
movingPhase['ydisp'] = ydisp

movingPhase['xdisp'][movingPhase['frame'] == 0.0] = np.nan
movingPhase['ydisp'][movingPhase['frame'] == 0.0] = np.nan
movingPhase['xvelocity'][movingPhase['frame'] == 0] = np.nan
movingPhase['yvelocity'][movingPhase['frame'] == 0] = np.nan
# movingPhase['xvelocity'][(movingPhase['xvelocity'] < 0.1) & (movingPhase['xvelocity'] > -0.1)] = np.nan
movingPhase['yvelocity'][(movingPhase['yvelocity'] < 0.0) & (movingPhase['yvelocity'] > -0.0)] = np.nan

movingPhase['xvelocity'][(movingPhase['xvelocity'] == 0.0)] = np.nan
movingPhase['yvelocity'][(movingPhase['yvelocity'] == 0.0)] = np.nan

filename = dirAnalysis+'/Position'+str(pos)+'_analysis.csv'
movingPhase.to_csv(filename, sep=",", index=False)



#%% Fig1. Boxplots of velocities inside and outside the lines

fig1, axes = plt.subplots(1,1, figsize=figsize)
df = movingPhase

x = 'activation'
y = 'yvelocity'
limityvel = 40

df['yvelocity'] *= df['yvelocity'].apply(lambda x : (x < limityvel))
df['yvelocity'] *= df['yvelocity'].apply(lambda x : (x > -limityvel))

axes = sns.boxplot(x = x, y=y, data=df, ax=axes,
                   medianprops={"color": 'darkred', "linewidth": 2}, 
                   boxprops={"edgecolor": 'k',"linewidth": 2, 'alpha' : 0.4})

axes = sns.swarmplot(x = x, y=y, data=df, ax=axes, hue = 'particle')


dfStat = df.dropna()

ufun.addStat_df(axes, dfStat, [('out', 'in')], y, test = 'Mann-Whitney', cond = x)

axes.axes.set_title(expt+"pos"+str(pos)+"_Y-Velocity of cells inside and outside the line",fontsize=titlefont)
axes.set_xlabel("In/Out of line",fontsize=xlabelfont)
axes.set_ylabel("Y-Velocity (um/hr)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_yvel-activation.png')
plt.show()

fig1bis, axes = plt.subplots(1,1, figsize=figsize)



axes = sns.boxplot(x = x, y=y, data=df, ax=axes,
                   medianprops={"color": 'darkred', "linewidth": 2}, 
                   boxprops={"edgecolor": 'k',"linewidth": 2, 'alpha' : 0.4})

axes = sns.swarmplot(x = x, y=y, data=df, ax=axes)


dfStat = df.dropna()

ufun.addStat_df(axes, dfStat, [('out', 'in')], y, test = 'Mann-Whitney', cond = x)

axes.axes.set_title(expt+"pos"+str(pos)+"_Avg_Y-Velocity of cells inside and outside the line",fontsize=titlefont)
axes.set_xlabel("In/Out of line",fontsize=xlabelfont)
axes.set_ylabel("Y-Velocity (um/hr)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_Avg_yvel-activation.png')
plt.show()

#%% Fig2. Y-velocities of cells inside/outside the lines over time, moving phase

fig2, axes = plt.subplots(1,1, figsize=figsize)
df = movingPhase

x = df['frame']*30/60
y = 'yvelocity'

axes = sns.lineplot(data = df, x = x, y = y, hue = 'activation', style = 'particle')

axes.axes.set_title(expt+"pos"+str(pos)+"_Y-Velocity of activated/non-activated cells over time (frame)",fontsize=titlefont)
axes.set_xlabel("Frames",fontsize=xlabelfont)
axes.set_ylabel("Y-Velocity (um/hr)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_yvel-time.png')
plt.show()

fig2bis, axes = plt.subplots(1,1, figsize=figsize)

axes = sns.lineplot(data = df, x = x, y = y, hue = 'activation')

axes.axes.set_title(expt+"pos"+str(pos)+"_Avg_Y-Velocity of activated/non-activated cells over time (frame)",fontsize=titlefont)
axes.set_xlabel("Time (hrs)",fontsize=xlabelfont)
axes.set_ylabel("Y-Velocity (um/hr)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_avg_yvel-time.png')
plt.show()
#%% Fig3. Trajectories of cells inside/outside the lines over time, moving phase

fig3, axes = plt.subplots(1,1, figsize=figsize)
df = movingPhase

x = df['frame']*30/60
y = 'y'

axes = sns.lineplot(data = df, x = x, y = y, hue = 'activation', style = 'particle')

axes.axes.set_title(expt+"pos"+str(pos)+"_Y-Displacement of activated/non-activated cells over time",fontsize=titlefont)
axes.set_xlabel("Time (hrs)",fontsize=xlabelfont)
axes.set_ylabel("Y-disp (um)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)
axes.set_xlim(0,110)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_y-time.png')
plt.show()

fig3bis, axes = plt.subplots(1,1, figsize=figsize)

axes = sns.lineplot(data = df, x = x, y = y, hue = 'activation')

axes.axes.set_title(expt+"pos"+str(pos)+"_Avg_Y-Displacement of activated/non-activated cells over time",fontsize=titlefont)
axes.set_xlabel("Time (hrs)",fontsize=xlabelfont)
axes.set_ylabel("Y-disp (um)",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)
axes.set_xlim(0,110)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_avg_y-time.png')
plt.show()


#%% Fig4. Histogram of velocities, inside/outside the lines

fig4, axes = plt.subplots(1,1, figsize=figsize)
df = movingPhase

x = 'yvelocity'

sns.histplot(data=df, x = x, binwidth=3, kde=True, hue = 'activation')

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_yvelHisto.png')

plt.show()

#%% Fig5. Fraction (inside/total) of cells populating the lines

fig5, axes = plt.subplots(1,1, figsize=figsize)
df = tracks 

y = 'fraction'
x = df['frame']*30/60

sns.lineplot(data=df, x = x, y = y)



axes.axes.set_title(expt+"pos"+str(pos)+" | Fraction of cell enrichment in time (mins)",fontsize=titlefont)
axes.set_xlabel("Time (hrs)",fontsize=xlabelfont)
axes.set_ylabel("Fraction of cells inside line",fontsize=ylabelfont)
axes.tick_params(labelsize=xtickfont)
axes.set_xlim(0, 60)

plt.savefig(dirFig+'/'+expt+'_pos'+str(pos)+'_lineEnrichmentvsTime.png')

plt.show()

plt.close('all')