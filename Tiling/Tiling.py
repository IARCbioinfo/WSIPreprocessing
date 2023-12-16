#!interpreter [optional-arg]
# -*- coding: utf-8 -*-

"""
Tiling allows you to divide a whole slide image (WSI) into patches. This script has been adapted to tile WSI in svs (Leica scanner) or
mrxs (3DHistech scanner) format. It automatically handles two magnifications of x20 or x40. The programme excludes tiles belonging to the background
or blurred area tiles, you can still save them using the SaveBackgroundTiles option. The tiles will be saved with the following tree:
- outputdir:
    - PatientID
        -accept (non-background tiles)
            - PathientID_HorizontalPositionOfTIleonWSI_VerticalPositionOfTIleonWSI.jpg
        - reject (background tiles if SaveBackgroundTiles option activated)
"""

from __future__ import division
from multiprocessing import Pool
import sys
import os
import argparse
# # necessary to add cwd to path when script run 
# # by slurm (since it executes a copy)
sys.path.append(os.getcwd()) 
import cv2
import numpy as np
from openslide import OpenSlide
from PIL import Image
from resizeimage import resizeimage
import random 
from glob import glob

__author__ = "Mathian Emilie"
__email__ = "mathiane@iarc.who.int"

def getGradientMagnitude(im):
    "Get magnitude of gradient for given image"
    ddepth = cv2.CV_32F
    dx = cv2.Sobel(im, ddepth, 1, 0)
    dy = cv2.Sobel(im, ddepth, 0, 1)
    dxabs = cv2.convertScaleAbs(dx)
    dyabs = cv2.convertScaleAbs(dy)
    mag = cv2.addWeighted(dxabs, 0.5, dyabs, 0.5, 0)
    return mag

def WSIToTIles(args, path_to_wsi):
    # Create outputs folder
    os.makedirs(os.path.join(args.outputdir), exist_ok=True)
    os.makedirs(os.path.join(args.outputdir, args.PatientID), exist_ok=True)
    os.makedirs(os.path.join(args.outputdir, args.PatientID, 'accept'), exist_ok=True)
    if args.SaveBackgroundTiles:
        os.makedirs(os.path.join(args.outputdir,  args.PatientID, 'reject'), exist_ok=True)

    imgfilename = path_to_wsi.split("/")[-1]
    # SVS: Leica scanner
    if imgfilename.find(".svs") != -1 or imgfilename.find("mrxs") != -1:
        img  = OpenSlide(path_to_wsi)
        print("WSI loaded")
        if imgfilename.find(".svs") != -1 :
            # Get magnification x40 or x20
            if str(img.properties.values.__self__.get('tiff.ImageDescription')).split("|")[1] == "AppMag = 40":
                # WSI mag = x40
                sz = args.TilesSize
                seq = args.TilesSize
            else:
                # WSI mag = x20
                sz = args.TilesSize / 2
                seq = args.TilesSize / 2
        # MRXS : 3DHiSTECH scanner
        elif  imgfilename.find("mrxs") != -1:
            if str(img.properties.values.__self__.get("mirax.GENERAL.OBJECTIVE_MAGNIFICATION")) == 40:
                # C-FLow and FastFlow
                sz = args.TilesSize 
                seq = args.TilesSize
            else: 
                sz = args.TilesSize / 2 
                seq = args.TilesSize / 2 
    [w, h] = img.dimensions
    nb_non_background_tiles = 0
    print("Creating tiles")
    for x in range(1, w, seq):
        for y in range(1, h, seq):
            try:
                img_r=img.read_region(location=(x,y), level=0, size=(sz,sz))
                img_r=img_r.convert("RGB")
                # Create tile
                img_r=img_r.resize((args.TilesSize,args.TilesSize),Image.ANTIALIAS)
                # Compute gradient magnitude
                pix = np.array(img_r)
                grad=getGradientMagnitude(pix)
                unique, counts = np.unique(grad, return_counts=True)
                mean_ch = np.mean(pix, axis=2)
                # Get number of bright pixel
                bright_pixels_count = np.argwhere(mean_ch > args.BrightPixel).shape[0]
                # Save non-background tiles:
                # Condition 1: proportion of bright pixels does not exceed args.PBakcgroundPixel of the tile
                # Condition 2: proportion of blurred pixels does not exceed args.PGradientMagnitude of the tile
                if bright_pixels_count <  args.TilesSize*args.TilesSize*args.PBakcgroundPixel and \
                 counts[np.argwhere(unique<=args.ThGradientMagnitude)].sum() < args.TilesSize*args.TilesSize*args.PGradientMagnitude: 
                    # Format of tiles filename: PathientID_HorizontalPositionOfTIleonWSI_VerticalPositionOfTIleonWSI.jpg
                    img_r.save( os.path.join(args.outputdir,  args.PatientID ,'accept', args.PatientID + "_" +  str(x) + "_" + str(y) + '.jpg'  ) , 'JPEG', optimize=True, quality=94)
                    nb_non_background_tiles += 1
                else:
                    if args.SaveBackgroundTiles:
                        img_r.save( os.path.join(args.outputdir, args.PatientID ,'reject', args.PatientID + "_" +  str(x) + "_" + str(y) + '.jpg'  ) , 'JPEG', optimize=True, quality=94) 
            except:
                # Region of the WSI not readable
                with open(f'errorReadingSlides_{args.PatientID}.txt', 'a') as f:
                    f.write('\n{}\t{}\t{}'.format(args.PatientID,x,y))
    print(f"Nn of non-background tiles created = {nb_non_background_tiles}")
if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser(description='Tiling WSI.')
    parser.add_argument('--WSIFolder', type=str, help="Directory where the WSIs are stored.")
    parser.add_argument('--outputdir', type=str, help='output directory where the tiles will be saved.')
    parser.add_argument('--PatientID', type=str, help='ID of the patient, supposed to be include in the filename of the WSI, eg. PatientID1.svs.')
    parser.add_argument('--TilesSize', type=int, default=384, help='Tile size in pixels. Note: Tiles are square.')
    parser.add_argument('--BrightPixel', type=int, default=220, help="Threshold beyond which a pixel is considered to be bright, ie. a background pixel.")
    parser.add_argument('--PBakcgroundPixel', type=float, default=0.8, help="If more than x%% of a tiles consists of bright pixels,it is considered a background tiles and will be excluded.")
    parser.add_argument('--ThGradientMagnitude', type=int, default=15, help="Threshold below which a tile is considered bluish and therefore excluded.")
    parser.add_argument('--PGradientMagnitude', type=float, default=0.6, help="If more than x%% of a tiles consists of blurred pixels,it is considered a blurred tiles and will be excluded.")
    parser.add_argument('--SaveBackgroundTiles', default=False, action='store_true', help="If specified the tiles balonging to the background while be saved in the folder names 'reject'")
    args = parser.parse_args()

    path_to_wsi = glob(f'{args.WSIFolder}/*/HES/*/x40/*/*/{args.PatientID}.svs')
    if len(path_to_wsi)>0:
        path_to_wsi = path_to_wsi[0]
        WSIToTIles(args, path_to_wsi)
    else:
        print("WSI not found")