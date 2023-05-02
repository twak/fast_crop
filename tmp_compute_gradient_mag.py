# import the necessary packages
import os
import sys

from pathlib import Path
import numpy as np
from skimage import exposure
import matplotlib.pyplot as plt
import cv2

from scipy.signal import convolve2d

'''
Update one dataset to match the histogram of another
'''

multi = True
octaves=6

def build_dataset_histo(dir):
	histo = np.zeros((3, 256), dtype=float)
	cdf = np.zeros((3, 256), dtype=float)

	histos = [] # np.zeros(256, dtype=float)

	for factor in range(0, octaves):
		histos.append(np.zeros(256, dtype=float))

	count = 0

	for image_file in os.listdir(dir):

		print(f"building histogram from {count}  {image_file}")

		horizontal = np.array([[1, -1]])
		vertical =  np.array([[1],[-1]])

		image = cv2.cvtColor(cv2.imread(os.path.join(dir, image_file)), cv2.COLOR_BGR2RGB)

		for factor in range (0,octaves):

			for filter_i, filter in enumerate ( [horizontal, vertical] ):
				translated_image = np.zeros(image.shape, dtype=np.ubyte)
				for c in range (3):
					cconv = np.abs( convolve2d(image[:,:,c], filter)[:,1:513] )
					translated_image[:,:,c] = cconv
					(hist, bins) = exposure.histogram(cconv.astype(np.ubyte), nbins=256, source_range="dtype")
					histos[factor] += hist / (2*3*image.shape[0]*image.shape[0])

				image = cv2.resize(image, (int(image.shape[0]/2), int(image.shape[1]/2)), interpolation=cv2.INTER_AREA)

			cv2.imwrite(os.path.join("/home/twak/Downloads", f"{factor}-{filter_i}-{Path(image_file).with_suffix(f'.png').name}"), cv2.cvtColor(translated_image, cv2.COLOR_RGB2BGR))

		count+=1

		if count > 0:
			break

	for o in range(0, octaves):
		histos[o] /= count

	return histos

def plot_histo (axs, histo,  col=0):
	maxx = histo.max()
	# cdf_max = cdf.max()
	bins = list(range(0, 256) )

	# for j in range(3):
	axs[col].plot(bins, histo / maxx)

syn_dir = "/home/twak/Downloads/winsyn_blossom/rgb"
syn_histo = build_dataset_histo(syn_dir)
gt_histo  = build_dataset_histo("/home/twak/Downloads/winlab_4_png/rgb") # sys.argv[2])

(fig, axs) = plt.subplots(nrows=octaves, ncols=1, figsize=(8, 20))

#combined = syn_histo-gt_histo

bins = list(range(0, 256))
size = 512

for o in range (octaves):

	axs[o].plot(bins, syn_histo[o])
	axs[o].plot(bins, gt_histo [o])

	# axs[1,o].plot(bins, (syn_histo[o] / syn_histo[o].max()) - (gt_histo[o]  / gt_histo[o] .max() ))

	base = 4

	g = lambda a: np.power ( a, base   )
	f = lambda a: np.power ( a, 1/base )
	axs[o].set_yscale('function', functions=(f,g))
	#axs[1].set_yscale('function', functions=(f,g))


	axs[o].set_ylim(0, 0.33)
	# axs[0].set_range()


	# plot_histo (axs, gt_histo   , gt_cdf   , col=0)
	# plot_histo (axs, syn_histo  , col=0)
	# plot_histo (axs, fixed_histo, fixed_cdf, col=2)

	# set the axes titles
	axs[o].set_title(f"{size}")
	# axs[0, 1].set_title("Syn")
	# axs[0, 2].set_title("Matched")
	# display the output plots
	size /= 2
plt.tight_layout()
plt.show()