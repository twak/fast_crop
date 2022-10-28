import glob
import os

import numpy as np
from PIL import Image
import process_labels

dataset_root = r'/home/twak/Downloads/winlab_1'

label_src = []
label_src.extend(glob.glob(os.path.join(dataset_root, "labels", "*.png")))

hist = np.zeros((12))
counts = np.zeros((12)) # images which have this element
total = 0

for f in label_src:

    print (f)
    label = np.asarray(Image.open(f, "r"))
    h = np.histogram(label, bins=12, range=(0,11), density=False)[0]
    counts += h > 0
    hist = hist + h

total = np.sum(hist)

for i in range ( len(hist) ):
    print ( "%s, %d, %d, %f" % (process_labels.LABEL_SEQ[i], counts[i], hist[i], hist[i]/float ( total ) ) )
    # print ("\n")
