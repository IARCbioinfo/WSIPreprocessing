#!interpreter [optional-arg]
# -*- coding: utf-8 -*-

"""
VahadaneNormalizationHES is used to articipate the saffron colouring method on HES tiles extracted from WSI, using the colour deconvolution method.
proposed by Vahadane et al ( IEEE Transactions on Medical Imaging, 2016 - https://ieeexplore.ieee.org/abstract/document/7460968).
More generally, the method can be used to remove the colour batch effect between WSIs from different hospitals. 
This program is a python adaptation of the original matplotlib program available at: https://github.com/abhishekvahadane/CodeRelease_ColorNormalization

Input directory structure:
-Non-normalized directory
    -Patient ID1
            - accept (non background tiles)
                    - patient_id_1x_y.jpg
            - reject (baackground tiles)

Output directory structure:
-Normalized directory
    -Patient ID2
            - accept (non background tiles)
                    - patient_id_1x_y.jpg
            - reject (baackground tiles if ApplyVahadaneOnBackgroundTiles specified) 

"""


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import spams
import cv2
from PIL import Image
import utils
from vahadane import vahadane
from sklearn.manifold import TSNE
import os
import pandas as pd
import argparse

global inputdir
global outputdir
import time
import datetime

__author__ = "Mathian Emilie"
__email__ = "mathiane@iarc.who.int"



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test set carcinoids for scanners.')
    parser.add_argument('--TargetTiles', type=str, help='HE stained Tiles used as reference, if the goal is to remove Safron staining')
    parser.add_argument('--inputdir', type=str, help="Directory where the tiles to normalized are saved")
    parser.add_argument('--PatientID', type=str,    help='Folder name matching with the patients ID, containing the tiles to normalized.')
    parser.add_argument('--outputdir', type=str, help='Directory where the tiles normalized through the Vahadane color deconvolution method will be saved')
    parser.add_argument('--ApplyVahadaneOnBackgroundTiles', default=False, action='store_true', help="If specified the tiles balonging to the background while be normalized")

    args = parser.parse_args()


    # directory_target   = '/home/mathiane/LNENWork/Tiles_HE_TCGA_LUAD_384_384'
    # TARGET_PATH_HE = directory_target  + '/F-TCGA-64-5781-01Z-00-DX1/accept/'+'TCGA-64-5781-01Z-00-DX1_25345_9985.jpg'
    # Get target tile
    target_imageHE = utils.read_image(args.TargetTiles)

    # Create Vahadane instance
    vhdHE = vahadane(STAIN_NUM=2, LAMBDA1=0.01, LAMBDA2=0.01, fast_mode=0, getH_mode=0, ITER=50)
    vhdHE.fast_mode=0;
    vhdHE.getH_mode=0;
    WtHE, HtHE = vhdHE.stain_separate(target_imageHE)
    vhdHE.setWt(WtHE); 
    vhdHE.setHt(HtHE); 

    # Create outputdir
    os.makedirs(os.path.join(args.outputdir), exist_ok=True)
    os.makedirs(os.path.join(args.outputdir, args.PatientID), exist_ok=True)
    os.makedirs(os.path.join(args.outputdir, args.PatientID, "accept"), exist_ok=True)
    if args.ApplyVahadaneOnBackgroundTiles:
        os.makedirs(os.path.join(args.outputdir, args.PatientID, "reject"), exist_ok=True)

    # Normalzed tiles
    ## Non-background tiles
    tiles_list = os.listdir(os.path.join(args.inputdir,args.PatientID,"accept"))
    for t in tiles_list:
            if t.find('jpg') != -1 :
                # Read src image
                src_img_path = os.path.join(args.inputdir,args.PatientID,"accept",  t)
                source_image = utils.read_image(src_img_path)
                pix = np.array(source_image)
                # Apply Vahadane color deconvolution
                Ws, Hs = vhdHE.stain_separate(source_image)
                res = vhdHE.SPCN(source_image, Ws, Hs)# 
                res =  Image.fromarray(res)
                # Save the normalized tile
                res.save( os.path.join(args.outputdir, args.PatientID, "accept",  t) , 'JPEG', optimize=True, quality=94) 
    if args.ApplyVahadaneOnBackgroundTiles:
        ## background tiles
        tiles_list = os.listdir(os.path.join(args.inputdir,args.PatientID,"reject"))
        for t in tiles_list:
                if t.find('jpg') != -1 :
                    # Read src image
                    src_img_path = os.path.join(args.inputdir,args.PatientID,"reject",  t)
                    source_image = utils.read_image(src_img_path)
                    pix = np.array(source_image)
                    # Apply Vahadane color deconvolution
                    Ws, Hs = vhdHE.stain_separate(source_image)
                    res = vhdHE.SPCN(source_image, Ws, Hs)# 
                    res =  Image.fromarray(res)
                    # Save the normalized tile
                    res.save( os.path.join(args.outputdir, args.PatientID, "reject",  t) , 'JPEG', optimize=True, quality=94) 