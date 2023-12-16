#!/bin/bash
python Tiling/Tiling.py \
--WSIFolder /path/to/WSI/HE/database \
--outputdir /path/where/tiles/will_be_saved \
--PatientID TNE_ID \
--TilesSize 384 \
--BrightPixel 220 \
--PBakcgroundPixel 0.8 \
--ThGradientMagnitude 15 \
--PGradientMagnitude 0.8 