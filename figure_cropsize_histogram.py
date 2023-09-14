import glob
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import process_labels

from pathlib import Path

# dataset_root = r"/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"
dataset_root = r"/media/twak/Saudi Data Raid/archinet_backup/data"
#dataset_root = r"C:\Users\twak\Downloads\egs_for_paper\"

# label_src = []
# label_src.extend(glob.glob(os.path.join(dataset_root, "labels", "*.png")))

buckets = 20
max = 10000

xes = np.zeros((buckets))
yes = np.zeros((buckets)) # images which have this element

total = 0

json_src = []
# json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_single_elements", "*", "*.json")))

np_data = None  # []

allx = []
ally = []

for json_file in json_src:
    print (json_file)

    prev = json.load(open(json_file, "r"))

    rects = prev["rects"]

    tags = []

    min_dim = 1000

    if "tags" in prev:
        tags = prev["tags"]

    if 'deleted' in tags:
        print("skipping deleted")
        continue



    for r in rects:

        if "window" not in r[1] and "glass_facade" not in r[1] and "shop" not in r[1] and "church" and "door" not in r[1] and "abnormal" not in r[1]:
            print("skipping not-a-window " + " ".join(tags))
            continue

        r = r[0]

        if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
            print("skipping small rect")
            continue

        # create a scatter plot of r[2] and r[3]
        # plt.scatter(r[2], r[3])

        allx.append(r[2])
        ally.append(r[3])

        h = np.histogram(r[2], bins=buckets, range=(0, max), density=False)[0]
        w = np.histogram(r[3], bins=buckets, range=(0, max), density=False)[0]

        xes = xes + w
        yes = yes + h

    # if len(allx) > 1000:
    #     break

total_w = np.sum(xes)
total_y = np.sum(xes)

plt.scatter(allx, ally, color="#86aade" ,  edgecolors='none',  alpha=0.002 )
plt.xlabel("x-resolution (pixels)")
plt.ylabel("y-resolution (pixels)")
plt.savefig("/home/twak/Downloads/crop_resolutions.png", dpi=300)
plt.show()

for i in range ( buckets ):
    print ( "%d, %f, %f" % (i, xes[i], yes[i] ) )
    # print ("\n")
