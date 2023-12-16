import cv2
import numpy as np


def read_image(path):
	try:
	    print(path)
	    img = cv2.imread(path)
	    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # opencv default color space is BGR, change it to RGB
	    p = np.percentile(img, 90)
	    img = np.clip(img * 255.0 / p, 0, 255).astype(np.uint8)
	    img[np.where((img==[0, 0, 0]).all(axis=2))] = [255,255,255]
	    return img
	except:
		return -1
