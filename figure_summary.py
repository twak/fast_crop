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

''' create the metadata_summary folder, with stats and crops '''

def crop_save_img(basename, count, batch, dataset_root, img):

    width = img.width
    height = img.height
    new_width = min(width, height)
    left = int(np.ceil((width - new_width) / 2))
    right = width - np.floor((width - new_width) / 2)
    top = int(np.ceil((height - new_width) / 2))
    bottom = height - int(np.floor((height - new_width) / 2))
    img = img.crop((left, top, right, bottom))
    img = img.resize((512, 512))  # , resample=resample)
    img.save(os.path.join(dataset_root, "metadata_summary", batch, f"{basename}_{count}.jpg"))


def wild(path, extn):

    out = []
    out.extend(glob.glob(os.path.join(path, f"*.{extn.lower()}")))
    if platform == "linux":
        out.extend(glob.glob(os.path.join(path, f"*.{extn.upper()}")))

    return out

def batch_summary(dataset_root, batch):

    summary_file = os.path.join(dataset_root, "metadata_summary", batch, "summary.json")
    if (os.path.exists(summary_file)):
        return # lazy!

    os.makedirs(Path(summary_file).parent, exist_ok= True)


    photo_src = wild( os.path.join( dataset_root, "photos", batch), "jpg" )

    stats = {}
    stats["jpgs"] = 0
    stats["raws"] = 0
    stats["invalid_jpgs"] = 0
    stats["megapixels"] = 0
    stats["rect_crops_files"] = len ( wild( os.path.join( dataset_root, "metadata_single_elements", batch), "json" ) )
    stats["rect_crops_win"] = 0
    stats["rect_crops_other"] = 0
    stats["label_files"] = len(wild(os.path.join(dataset_root, "metadata_window_labels", batch), "json")) + len(wild(os.path.join(dataset_root, "metadata_window_labels_2", batch), "json"))
    stats["labelled_windows"] = 0
    stats["soft_deleted"] = 0

    for photo_file in photo_src:

        pp = Path(photo_file)
        print (pp.name)
        basename = os.path.splitext(pp.name)[0]
        # count = 1

        img = Image.open(photo_file)

        try:
            img.verify()
        except Exception as e:
            print (e)
            stats["invalid_jpgs"] += 1
            continue

        img = Image.open(photo_file) # reopen after validate
        img = ImageOps.exif_transpose(img)


        rect_file = os.path.join(dataset_root, "metadata_single_elements", batch,  basename+".json" )
        if os.path.exists(rect_file):
            prev = json.load(open(rect_file, "r"))
            rects = prev["rects"]

            tgs = []
            if "tags" in prev:
                tgs = prev["tags"]
            if 'deleted' in tgs:
                stats["soft_deleted"] +=1
                continue

            for r in rects:
                if tags.window not in r[1] and tags.glass_facade not in r[1] and tags.shop not in r[1] and tags.church not in r[1] and tags.abnormal not in r[1]:
                    stats["rect_crops_other"] += 1
                else:
                    stats["rect_crops_win"] += 1

        stats["megapixels"] += img.width * img.height

        stats["jpgs"] +=1

        for extension in process_labels.RAW_EXTS:
            if Path(photo_file).with_suffix("."+extension).exists():
                stats["raws"] += 1

        label_file = os.path.join(dataset_root, "metadata_window_labels", batch, basename+".json" )
        if os.path.exists(label_file):
            labelled_areas = json.load(open(label_file, "r"))
            stats["labelled_windows"] += len (labelled_areas)

        label_file = os.path.join(dataset_root, "metadata_window_labels_2", batch, basename+".json" )
        if os.path.exists(label_file):
            labelled_areas = json.load(open(label_file, "r"))
            stats["labelled_windows"] += len (labelled_areas)

    with open(summary_file, "w") as of:
        json.dump(stats, of)



if __name__ == "__main__":

    dataset_root = r"."

    for batch in os.listdir(os.path.join(dataset_root, "photos")):
        print(" >>>>>>>>>>> "+ batch)
        batch_summary (dataset_root, batch)

    keys = ["jpgs", "raws", "invalid_jpgs", "megapixels", "rect_crops_files", "rect_crops_win", "rect_crops_other", "label_files", "labelled_windows","soft_deleted"]

    print(f"stats!, ", end='')
    for key in keys:
        print(f"{key}, ", end='')
    print()

    for batch in os.listdir(os.path.join(dataset_root, "metadata_summary")):
        summary_file = os.path.join(dataset_root, "metadata_summary", batch, "summary.json")
        if os.path.exists(summary_file):
            with open(summary_file, "r") as of:
                stats = json.load(of)
                print(f"{batch}, ", end='')
                for key in keys:
                    print(f"{stats[key]}, ", end='')
                print()






