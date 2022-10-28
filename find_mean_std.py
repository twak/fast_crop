import glob
import os

import numpy as np
from PIL import Image

json_src = []
json_src.extend(glob.glob(os.path.join("/home/twak/Downloads/photo", "*.jpg")))

np_data = []

for f in json_src:
    print (f)
    np_data.append(np.asarray(Image.open(f, "r")))

all_data = np.concatenate(tuple(np_data), 0)
print(f"mean [{np.mean(all_data, axis=(0, 1))}] std [{np.std(all_data, axis=(0, 1))}]")