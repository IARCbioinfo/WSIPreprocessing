# WSIPreprocessing
The whole slide image (WSI) pre-processing repository includes the patching process and the Vahadane colour normalisation method. These pre-processing are highly recomanded before applying a deep-learning method.

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
