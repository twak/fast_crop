import os
import json
import numpy as np

mious = []
b2 = []

for f in os.listdir("/home/twak/Downloads/riyal_label_egs"):

    mious.append ( float ( f.split("-")[0] ) )

hist, bins = np.histogram(mious, bins=16, range=(0, 100), density=False)


print(f"mean: {np.mean(mious)}")

for i in range ( len (hist) ):
    print (bins[i], end=", ")

    print (hist[i], end=", ")

    print()


