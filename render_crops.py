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
import svgwrite
from PIL import ImageOps
import numpy as np
from sys import platform
import hashlib
from PIL.Image import Transpose

import process_labels

def render_crops(images, output_dir, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution=512, quality=95):
    '''
    renders each window crop to a uniquely named file
    '''

    os.makedirs(output_dir, exist_ok=True)

    fm = 'w' if clear_log else 'a'
    log = open( os.path.join ( output_dir, 'log.txt'), fm)

    def save(im, out_name, subdir=None):

        if len (im.getbands() ) > 3: # pngs..
             im = im.convert("RGB")

        if im.width == 0 or im.height == 0:
            print("skipping zero sized rect in %s" % out_name)
            return

        md5hash = hashlib.md5(im.tobytes())
        jpg_out_file = "%s.png" % md5hash.hexdigest()
        log.write("\"%s\"\n" % jpg_out_file)

        if sub_dirs:
            out_path = os.path.join(output_dir, subdir, jpg_out_file)
        else:
            out_path = os.path.join(output_dir, jpg_out_file)

        im.save(out_path, format="PNG", quality=quality)

    if not crop_mode in process_labels.VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(process_labels.VALID_CROPS)))
        return

    min_dim = 512
    count = 0

    print (f"found {len(images)} jpgs")

    for im_file in images:


        print ('processing %s...' % im_file)

        out_name, out_ext = os.path.splitext ( os.path.basename(im_file) )
        out_ext = out_ext.lower()

        batch_name = Path(im_file).parent.name

        if sub_dirs:
            # sub_dir = os.path.split ( os.path.split(im_file)[0] )[1]
            dir = os.path.join(output_dir, batch_name)
            os.makedirs( dir, exist_ok=True)


        json_file = Path(im_file).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch_name).joinpath(f"{out_name}.json")

        if os.path.exists(os.path.join (".",json_file ) ): # there is a crop file

            prev = json.load(open(json_file, "r") )
            im = process_labels.open_and_rotate( im_file, prev )
            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            for r in rects:

                if not ( "window" in r[1] or "door" in r[1] or "glass_facade" in r[1] or "shop" in r[1] or "church" in r[1] or "abnormal" in r[1] ): # types of window
                    continue

                c = r[0]

                if c[2] - c[0] < min_dim or c[3] - c[1] < min_dim:
                    print("skipping small rect")
                    continue

                log.write("%s [%d, %d, %d, %d]\n" % (im_file, c[0], c[1], c[2], c[3]) )

                crop_im = im.crop( ( c[0], c[1], c[2], c[3] ) )
                crop_im = process_labels.crop(crop_im, resolution, crop_mode)

                save(crop_im, out_name, batch_name if sub_dirs else None)
                count = count + 1

                print(f"count {count}")

        else:
            print("no metadata_single_element crop file, skipping")

    log.close()



if __name__ == "__main__":

    photo_src = []

    photo_src.extend(glob.glob(r'./photos/*/*.jpg'))

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
    else:
        photo_src.extend(glob.glob(r'./photos/*/*.JPG'))
        dataset_root = r"/home/twak/archinet/data"

    output_folder = f"./dataset_cook_{time.time()}/"

    os.makedirs(output_folder, exist_ok=True)

    render_crops(photo_src, output_folder, crop_mode="square_crop", resolution=512, quality=95, sub_dirs=True)