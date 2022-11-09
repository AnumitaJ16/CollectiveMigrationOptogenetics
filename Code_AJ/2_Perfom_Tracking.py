# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 16:01:26 2022

@author: anumi
"""

# Load python modules used in the following
import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import scipy
from skimage import measure # to get object contours from masks

import tqdm
import pims
import trackpy as tp  # we use trackpy module for tracking

import imagecodecs
import napari

#%% # I. Load segmentation results


os.chdir("D:\Hugo\Migration")  # root dir containg Predictions and Images Path
predictions_path = "Predictions/Sd_versatile_Position2_2048x2048.tif"
corresponding_imgs = "Position2/Position2.tif"

predictions = imageio.volread(predictions_path)
# predictions = pims.open(predictions_path)
imgs = imageio.volread(corresponding_imgs)

#%% II. Get objects from contours

#%%%% Retrieve object contours using skimage
# importing colors
import matplotlib.colors as mcolors
by_hsv = [(tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                         name)
                        for name, color in mcolors.TABLEAU_COLORS.items()]
names = [name for hsv, name in by_hsv]

# retrieving contours at each frame
print("This step should take around 1 minutes for 50 frames (50 it.)")
all_contours = []
for i, m in tqdm.tqdm(enumerate(predictions)):  # iterating on frames

    all_contours_at_this_frame = []
    for gray_level in np.unique(m)[1:]:  # iterating on grey levels in each frame. Don't take 0 as it is the background
        obj = np.array(m == gray_level, dtype=np.uint8)  # only pixels with this intensity = one specific object
        contours = measure.find_contours(obj, level=0.99)  # list of contours

        if len(contours) > 1:
            print(f"CAUTION: More than one object detected per grey level : {len(contours)} objects!")

        all_contours_at_this_frame.append(contours[0])  # only one object per grey level, list of objects per frame
    all_contours_at_this_frame = np.array(all_contours_at_this_frame, dtype=np.object)  # one array per frame
    all_contours.append(all_contours_at_this_frame) 

all_contours = np.array(all_contours, dtype=np.object)  # array of frames of objects

print(f"Done. Retrieved contours for {all_contours.shape[0]} frames.")

# Plot several frames with the object and the retrieved contours.
print("Sanity check : the contours should be well superimposed with the objects.")
init_idx, nb_frames = 0, 3
fig, axes = plt.subplots(1, nb_frames, figsize=(8 * nb_frames, 8))
for idx, (mask, contours, ax) in enumerate(zip(predictions[init_idx:init_idx+nb_frames], all_contours[init_idx:init_idx+nb_frames], axes)):
    ax.set_title(f"Frame {init_idx + idx}")
    ax.imshow(mask)

    for contour in contours:
        ax.plot(contour[:, 1], contour[:, 0])

#%%%% From the contours retrieve the centroid (barycenter) of each object

# retrieve all barycenters and build a datastructure for trackpy
positions_at_frames = []
for i, frame in enumerate(all_contours):
    for cell in frame:
        positions_at_frames.append({"frame": i, "x": np.sum(cell[:, 1]) / cell.shape[0], "y": np.sum(cell[:, 0]) / cell.shape[0]})
positions_per_frame = pd.DataFrame(positions_at_frames)

# check the shape
print(positions_per_frame.shape)

# Display the image and plot the barycenters to check if they're correctly positioned
nb_imgs = 4
fig, ax = plt.subplots(1, nb_imgs, figsize=(8 * nb_imgs, 8))

print("The barycenters (coloured dots) should be well superimposed with the objects.")

for i, (contour_im, im) in enumerate(zip(all_contours[:nb_imgs], imgs[:nb_imgs])):
#     ax[i].imshow(cv2.resize(im, (512, 512)), cmap="gray", origin="lower")
    ax[i].imshow(im, cmap="gray", origin="lower")
    for idx, cell in positions_per_frame[positions_per_frame["frame"] == i].iterrows():
        x, y = cell["x"], cell["y"]
        ax[i].scatter(x, y)
    ax[i].axis("off")
    ax[i].set_title(f"Frame {i}")
    

positions_per_frame.head()

#%% III. Peform tracking using the surface and position of each cell at each time point

# perform the tracking step
max_search_radius = 300  # maximum distance made by
tracks = tp.link(positions_per_frame, max_search_radius, memory=1)

# reformat the tracking results to display them
tracks_to_napari = []
for i, track in tracks.iterrows():
    tracks_to_napari.append({"ID": track["particle"], "Frame": track["frame"], "X": track["y"], "Y": track["x"]})
tracks_to_napari = pd.DataFrame(tracks_to_napari)

tracks_to_napari.head()

#%% Saving tracking results to a csv file

# saving the tracking results
save_path = "D:/Hugo/Migration/Position2_tracking_results.csv"
tracks.to_csv(save_path, sep=",", index=False)

#%% Diplaying tracks using Napari
print("Displaying tracks in napari (a new window should open).")

viewer = napari.view_image(imgs, name="Images", opacity=0.8)
viewer.add_image(predictions * 255, opacity=1.0, colormap="blue", blending="additive", name="Segmentation")
viewer.add_tracks(tracks_to_napari, name="Tracks")