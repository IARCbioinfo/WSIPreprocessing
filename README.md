# WSIPreprocessing
The whole slide image (WSI) pre-processing repository includes the patching process and the Vahadane colour normalisation method. These pre-processing steps are strongly recommended before applying a deep learning method.

## Tiling 
- **Description:** Divide WSI to image patches called tiles.
- **See:** `Tiling` folder
- 🎯 **Usage:** `python Tiling/Tiling.py --WSIFolder /path/to/WSIs --outputdir /path/where/tiles/will/saved --PatientID PatientID|WSI_basename `
- **Help:** `python Tiling/Tiling.py --help`
- **Note:**
	- This program handles WSI in svs format (Leica scanner) and mrxs format (3DHistech scanner)
	- It automatically handles x40 and x20 magnification
	- PatientID argument is expected to be the basename of the WSI file *eg: if the WSI filename is patient_id1.svs then PatientID must be patient_id1*
- Configuration and examples:
	- The command lines used to pre-process the Ki-67, PHH3 and HE/HES WSIs from the ESMO Open slides are available in the `Tiling/config` 

## Vahadane color normalization method
- **Description:** Python implementation of the color deconvolution methods from Vahadane et al (IEEE Trans Med Imaging, 2016 - https://github.com/abhishekvahadane/CodeRelease_ColorNormalization). This method can be used to artificially removed saffron stain on HES tiles extracted from WSI, and more generally to normalised color between tiles of WSIs coming from different hospitals.
- **See:** `VahadaneColorNorm` folder
- 🎯 **Usage:** `python VahadaneColorNorm/ApplyVahadaneNormalization.py --TargetTile /path/to/reference/tile.jpg  --inputdir /path/to/tiles/directory --PatientID FolderNameOfTilesToNormalized --outputdir /path/where/tiles/Normalised/will_be_saved`
- **Help:** `python VahadaneColorNorm/ApplyVahadaneNormalization.py --help`
- **Note:**
	- The normalised tiles will be of the same sized as the non-normalised tiles
- **Structure input directory**:
```
- Non-normalized tiles directory
    - Patient ID1
            - accept (non background tiles)
                    - patient_id_1x_y.jpg
            - reject (baackground tiles)
```

- **Structure output directory**::
```
- Normalized tiles directory
    - Patient ID2
            - accept (non background tiles)
                    - patient_id_1x_y.jpg
            - reject (baackground tiles if ApplyVahadaneOnBackgroundTiles specified)
```