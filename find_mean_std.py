import glob
import os
import random
import sys

import numpy as np
from PIL import Image

json_src = []
json_src.extend(glob.glob(os.path.join(sys.argv[1], "*.png")))
json_src.extend(glob.glob(os.path.join(sys.argv[1], "*.jpg")))

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
    print(f"mean,std: [{np.mean(all_data, axis=(0, 1))}], [{np.std(all_data, axis=(0, 1))}]")
else:
    print("no images found :(")