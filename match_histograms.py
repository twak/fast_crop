# import the necessary packages
import os
import sys

from pathlib import Path
import numpy as np
from skimage import exposure
import matplotlib.pyplot as plt
import cv2

'''
Update one dataset to match the histogram of another
'''

multi = True

def build_dataset_histo(dir):
	histo = np.zeros((3, 256), dtype=float)
	cdf = np.zeros((3, 256), dtype=float)
	for i, image in enumerate ( os.listdir(dir) ):
		print(f"building histogram from {i}  {image}")
		# convert the image from BGR to RGB channel ordering
		image = cv2.cvtColor(cv2.imread(os.path.join(dir, image)), cv2.COLOR_BGR2RGB)
		for j in range(3):
			(hist, bins) = exposure.histogram(image[..., j], nbins=256, source_range="dtype")
			histo[j] += hist

	for j in range(3):
		cdf[j] = np.cumsum(histo[j])

	# cum /= len (os.listdir(dir))
	return histo,cdf/cdf.max()

def plot_histo (axs, histo,  cdf, col=0):
	maxx = histo.max()
	# cdf_max = cdf.max()
	bins = list(range(0, 256) )

	for j in range(3):
		axs[j, col].plot(bins, histo[j] / maxx)
		axs[j, col].plot(bins, cdf[j])

#https://github.com/scikit-image/scikit-image/blob/05427a08bce517aec855d4ca63ad0c98e5808955/skimage/exposure/histogram_matching.py#L6
def apply_histo(current_cum, new_cum, image_file):

	# convert the image from BGR to RGB channel ordering
	image = cv2.cvtColor(cv2.imread(image_file), cv2.COLOR_BGR2RGB)

	translated_image = np.zeros((512, 512, 3), dtype=np.float32)

	for j in range(3):
		quintiles = current_cum[j][ image[:, :, j].reshape(-1)]
		translated_image[:,:,j] = np.interp(quintiles, new_cum[j], np.arange(256) ).reshape((512, 512))

	cv2.imwrite( os.path.join (sys.argv[3], Path(image_file).with_suffix('.png').name), cv2.cvtColor(translated_image, cv2.COLOR_RGB2BGR))

	return translated_image


syn_dir = sys.argv[1] # "/home/twak/Downloads/winsyn_blossom/rgb"
syn_histo, syn_cdf = build_dataset_histo(syn_dir)
gt_histo, gt_cdf, = build_dataset_histo(sys.argv[2])
os.makedirs(sys.argv[3], exist_ok=True)

for i, image in enumerate ( os.listdir(syn_dir) ):
	print(f"processing {i}  {image}")
	apply_histo(syn_cdf, gt_cdf, os.path.join (syn_dir, image))

if False:

	fixed_histo, fixed_cdf = build_dataset_histo(sys.argv[3])

	(fig, axs) = plt.subplots(nrows=3, ncols=3, figsize=(8, 8))

	for j, color in enumerate(["red","green","blue"]):
		axs[j, 0].set_ylabel(color)

	plot_histo (axs, gt_histo   , gt_cdf   , col=0)
	plot_histo (axs, syn_histo  , syn_cdf  , col=1)
	plot_histo (axs, fixed_histo, fixed_cdf, col=2)

	# set the axes titles
	axs[0, 0].set_title("GT")
	axs[0, 1].set_title("Syn")
	axs[0, 2].set_title("Matched")
	# display the output plots
	plt.tight_layout()
	plt.show()