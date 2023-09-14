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
import fast_crop_tags as tags

import process_labels

def wild(path, extn):

    out = []
    out.extend(glob.glob(os.path.join(path, f"*.{extn.lower()}")))
    if platform == "linux":
        out.extend(glob.glob(os.path.join(path, f"*.{extn.upper()}")))

    return out

def batch_summary(dataset_root, batch):

    photo_src = wild( os.path.join( dataset_root, "photos", batch), "jpg" )

    for photo_file in photo_src:

        pp = Path(photo_file)
        print (pp.name)
        basename = os.path.splitext(pp.name)[0]
        # count = 1

        rect_file = os.path.join(dataset_root, "metadata_single_elements", batch,  basename+".json" )
        if not os.path.exists(rect_file):
            print (photo_src)

if __name__ == "__main__":

    dataset_root = r"."

    for batch in os.listdir(os.path.join(dataset_root, "photos")):
        if os.path.isdir(os.path.join(dataset_root, "photos", batch)) and not "synthetic" in batch:
            batch_summary (dataset_root, batch)
