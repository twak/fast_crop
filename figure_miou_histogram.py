import os
import json
import numpy as np

mious = []
b2 = []

for f in os.listdir("/home/twak/Downloads/most_improved/difference"):

    mious.append ( float ( f.split("_")[0] ) )

hist, bins = np.histogram(mious, bins=32, range=(-100, 100), density=False)


print(f"mean: {np.mean(mious)}")

for i in range ( len (hist) ):
    print (bins[i], end=", ")

    print (hist[i], end=", ")

    print()


