import glob
import json
import os

import numpy as np
from PIL import Image
import process_labels

from pathlib import Path

dataset_root = r"/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"

label_src = []
label_src.extend(glob.glob(os.path.join(dataset_root, "labels", "*.png")))

buckets = 16
max = 8000

xes = np.zeros((buckets))
yes = np.zeros((buckets)) # images which have this element

total = 0

json_src = []
# json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

np_data = None  # []

for json_file in json_src:
    batch_name = Path(json_file).parent.name

    with open(json_file, "r") as f:
        data = json.load(f)

    # crop to each defined region
    for crop_name, crop_data in data.items():
        crop_bounds = crop_data["crop"]

        h = np.histogram(crop_bounds[0], bins=buckets, range=(0, 8000), density=False)[0]
        w = np.histogram(crop_bounds[0], bins=buckets, range=(0, 8000), density=False)[0]

        xes = xes + w
        yes = yes + h


total_w = np.sum(xes)
total_y = np.sum(xes)


for i in range ( buckets ):
    print ( "%s, %d, %d, %f" % (i, total_w[i], total_y[i]  ) )
    # print ("\n")
