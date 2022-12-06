# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 15:17:48 2022

@author: Hugo, Hersen Team PCC

To use this code, run the following in the Anaconda Powershell:

Before activating environment:
conda install -c conda-forge spyder-kernels

Then the following lines below:
conda create -y -n napari-env -c conda-forge python=3.9
conda activate napari-env
python -m pip install "napari[all]"
conda install seaborn pandas tensorflow statsmodels imageio tifffile tqdm pims
conda install -c conda-forge pyautogui
pip install csbdeep pims trackpy
pip install opencv-python
pip install stardist

Make sure to have your grahical backend as Inline and not Qt, as cellpose affects the Qt package version.
"""

# required modules : numpy, matplotlib, stardist, tqdm, tifffile, csbdeep, cv2

from __future__ import print_function, unicode_literals, absolute_import, division
import sys
import h5py
import numpy as np
import matplotlib
matplotlib.rcParams["image.interpolation"] = None
import matplotlib.pyplot as plt
# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'

import os
import imageio
from glob import glob
from tqdm import tqdm
from tifffile import imread
from csbdeep.utils import Path, normalize

from stardist import fill_label_holes, random_label_cmap, calculate_extents, gputools_available
from stardist.matching import matching, matching_dataset
from stardist.models import Config2D, StarDist2D, StarDistData2D

import cv2
from skimage.transform import resize
import time

import UtilityFunctions as ufun

lbl_cmap = random_label_cmap()

#%% 0. Define experiment and position you want to process

dates = '21-07-22'
pos = 3

#%% I. Load the images

expt = ufun.date2expt(dates)
imgs = imageio.volread('D:/Anumita/CollectiveMigrationData/Raw/' + expt + '/Position' + str(pos) + '.tif')

batch = []
for im in imgs:
    batch.append(cv2.resize(im, (220, 220)))
imgs = np.array(batch)

print(imgs.shape)

#%% II. Load the segmentation model
model = StarDist2D.from_pretrained('2D_versatile_fluo')

#%% III. Check predictions on a single image
# take one image
img = normalize(imgs[2])
print(img.shape)

# make prediction
labels, details = model.predict_instances(img)
nb_detected_cells = np.unique(labels).size

# display predictions
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.imshow(img, clim=(0,1), cmap='gray')
ax.imshow(labels, cmap=lbl_cmap, alpha=0.5)
ax.set_title(f"Number of detected cells: {nb_detected_cells}.")

#%% IV. Make predictions on the full dataset

# CHANGE SAVE PATH here
saveDir = 'D:/Anumita/CollectiveMigrationData/Predictions/'+expt
savePath = saveDir+'/Predictions_Position'+str(pos)+'.tif'

try:
    os.mkdir(saveDir)
except:
    pass

    
batch_predictions = []
t0 = time.time()
for im in imgs:
    labels, _ = model.predict_instances(normalize(im))
    batch_predictions.append(cv2.resize(labels, (2048, 2048), interpolation=cv2.INTER_NEAREST ))  # resize the mask to 2048x2048, without interpolation
#     batch_predictions.append(labels)  # if the above doesn't work, and resize in ImageJ after (with interpolation == None)
predictions = np.array(batch_predictions, dtype=np.uint8)
print(f"Predictions duration : {round(time.time() - t0, 2)} sec.")

print(predictions.shape)
    
imageio.volwrite(savePath, predictions)