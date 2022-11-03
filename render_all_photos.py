import copy
import glob
import hashlib
import json

# from the index file when we created the crops for the labellers to our src coordinate system
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
from PIL import ImageOps
import numpy as np
from sys import platform
import hashlib



def process(jpg_file, out_dir, include_labelled=False, res=512):

    path = Path(jpg_file)
    # check
    if not include_labelled:
        if path.parent.parent.joinpath("metadata_window_labels").joinpath(os.path.splitext(path.name)[0]+".json").is_file():
            print("skipping labelled: "+jpg_file)
            return

    img = Image.open(jpg_file, "r")

    width = img.size[0]
    height = img.size[1]

    new_width = min(width, height)

    left = int(np.ceil((width - new_width) / 2))
    right = width - np.floor((width - new_width) / 2)

    top = int(np.ceil((height - new_width) / 2))
    bottom = height - int(np.floor((height - new_width) / 2))

    img = img.crop((left, top, right, bottom))

    img = img.resize((res, res)) #, resample=resample)

    md5hash = hashlib.md5(img.tobytes())
    img.save(os.path.join(out_dir, f"{md5hash}.jpg"))

    print (f"saved {jpg_file} to {md5hash}.jpg")

if platform == "win32":
    dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
else:
    dataset_root = r"/mnt/vision/data/archinet/data"

out_dir = r"/mnt/vision/data/archinet/crops_512_20221103"
os.makedirs(out_dir)

jpgs = []
jpgs.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.jpg")))
if platform == "linux":
    jpgs.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.JPg")))

for i, img in enumerate( jpgs ):
    print(f"{i}/{len(jpgs)}")
    process(img, out_dir)