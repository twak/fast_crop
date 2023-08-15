import glob
import os
import random
import sys

import numpy as np
from PIL import Image

json_src = []
json_src.extend(glob.glob(os.path.join(sys.argv[1], "*.png")))
json_src.extend(glob.glob(os.path.join(sys.argv[1], "*.jpg")))

if len(sys.argv) > 3:
    print (f"using split file {sys.argv[3]}")
    with open(os.path.join(dataset_root, sys.argv[3]), "r") as f:
        for line in f:
            label_src.append(os.path.join(dataset_root, "labels", f"{line[:-1]}.png"))

print(f"{len(json_src)} images found")
random.shuffle(json_src)

if len(sys.argv) > 2:
    print(f"using {sys.argv[2]} images for computation")
    json_src = json_src[:int(sys.argv[2])]


if len(json_src) > 0:

    np_data = []

    for f in json_src:
        print (f)
        np_data.append(np.asarray(Image.open(f, "r")))

    all_data = np.concatenate(tuple(np_data), 0)
    mean = np.mean(all_data, axis=(0, 1))
    std  = np.std (all_data, axis=(0, 1))
    print(f"mean=[{mean[0]}, {mean[1]}, {mean[2]}], std=[{std[0]}, {std[1]}, {std[2]}],")
    # print(f"mean,std: [{np.mean(all_data, axis=(0, 1))}], [{np.std(all_data, axis=(0, 1))}]")
else:
    print("no images found :(")