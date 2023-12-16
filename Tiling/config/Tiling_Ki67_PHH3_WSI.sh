#!/bin/bash
python Tiling/Tiling.py \
--WSIFolder /path/to/WSI/Ki67orPHH3/database \
--outputdir /path/where/tiles/will_be_saved \
--PatientID TNE_ID \
--TilesSize 256 \
--BrightPixel 220 \
--PBakcgroundPixel 0.7 \
--ThGradientMagnitude 15 \
--PGradientMagnitude 0.8 