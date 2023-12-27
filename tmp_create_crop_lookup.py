
import copy
import glob
import hashlib
import json
import os
import random
import shutil
import time
from collections import defaultdict
from os import path
from pathlib import Path
import PIL
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import svgwrite
from PIL import ImageOps
import numpy as np
from sys import platform
import hashlib
from PIL.Image import Transpose
import pickle

def add (label_json_file, lookup):

    jp = Path(label_json_file)

    if os.stat(label_json_file).st_size == 0: # while the labelling is in progress, some label files are empty placeholders.
        print (f"skipping empty label file {label_json_file}")
        return

    with open(label_json_file, "r") as f:
        data = json.load(f)

    c = 0
    for crop_name, crop_data in data.items():
        print(f"           {crop_name}")
        crop_name = crop_name.replace(".jpg", "")
        lookup[crop_name] = os.path.join ( jp.parent.name, jp.name[:-5] )
        c += 1

    return c

json_src = []
json_src.extend(glob.glob(r'./metadata_window_labels/*/*.json'))
json_src.extend(glob.glob(r'./metadata_window_labels_2/*/*.json'))

dataset_root = "."

lookup = {}
count = 0

for j in json_src:
    print( j )
    count += add(j, lookup)

print (f"found {count}")

with open('/home/twak/Downloads/crop2path2.pkl', 'wb') as fp:
    pickle.dump(lookup, fp)


