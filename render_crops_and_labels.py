import copy
import glob
import hashlib
import json

# from the index file when we created the crops for the labellers to our src coordinate system
import os
import random
import shutil
import sys
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
import concurrent.futures

import process_labels

def render_labels_per_crop( dataset_root, json_file, output_folder, reses=[512], mode='None', render_svg=False):
    '''
    Render out a labelled dataset. RGB labels and greyscale labels.
    '''

    if not mode in process_labels.VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(process_labels.VALID_CROPS)))
        return

    out = []
    colors = process_labels.colours_for_mode(process_labels.GREY_NO_DOOR)
    photo_file = process_labels.find_photo_for_json(dataset_root, json_file )

    for res in reses:
        os.makedirs(os.path.join(output_folder, f"{res}px", "rgb"   ), exist_ok=True)
        os.makedirs(os.path.join(output_folder, f"{res}px", "labels"), exist_ok=True)

    if render_svg:
        os.makedirs(os.path.join(output_folder, "svg"), exist_ok=True)

    batch_name = Path(json_file).parent.name

    country = process_labels.country_from_batch(dataset_root, batch_name)

    if  os.stat(json_file).st_size == 0: # while the labelling is in progress, some label files are empty placeholders.
        print ("skipping empty label file")
        return

    with open(json_file, "r") as f:
        data = json.load(f)

    photo = process_labels.open_and_rotate( os.path.join(dataset_root, photo_file), data )

    label_mode = "L" # greyscale

    # crop to each defined region
    for crop_name, crop_data in data.items():

        crop_bounds = crop_data["crop"]
        crop_photo =photo.crop (crop_bounds)

        label_img = Image.new(label_mode, (crop_photo.width, crop_photo.height))
        draw_label_photo = ImageDraw.Draw(label_img, label_mode)
        draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=colors["none"] )
        base_name = os.path.splitext(crop_name)[0]

        if isinstance( crop_data["labels"], dict ): # metadata_window_labels / part 1, render each category separately
            for cat, polies in crop_data["labels"].items():
                for poly in polies:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon( poly, colors[cat])
        else: # metadata_window_labels_2 / part 2, render in order
            for catl in crop_data["labels"]:
                cat = catl[0]
                for poly in catl[1]:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon(poly, colors[cat])

        for res in reses:
            # crop down
            crop_photo_r = process_labels.crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
            label_img_r  = process_labels.crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")

            print(f"rendering crops from {json_file} @ {res}:{mode}  = {base_name}")

            crop_photo_r.save(os.path.join(output_folder, f"{res}px", "rgb"   , base_name + ".jpg"), quality=90)
            label_img_r .save(os.path.join(output_folder, f"{res}px", "labels", base_name + ".png"))

        if render_svg:

            dwg = svgwrite.Drawing(os.path.join(output_folder, "svg", crop_name + ".svg"), profile='tiny')
            dwg.add(dwg.text(crop_name, insert=(0, 0.2), fill='black'))

            for cat, polies in crop_data["labels"].items():
                for poly in polies:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon(poly, colors[cat])
                    dwg.add(dwg.polygon(poly, fill=f'rgb({colors[cat][0]},{colors[cat][1]},{colors[cat][2]})'))

            dwg.save()

        out.append((country, base_name))

    return out



if __name__ == "__main__":

    # if platform == "win32":
    dataset_root = "." #sys.argv[1]
        # dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
    # else:
    #     dataset_root = r"/home/twak/archinet/data"

    output_folder = f"./metadata_cook/winsyn_cook_no_door_9k_{time.time()}/"

    os.makedirs(output_folder, exist_ok=True)

    json_src = []
    # json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels_2", "*", "*.json")))
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

    if True: # threaded
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as _pool:

            futures = [_pool.submit( render_labels_per_crop, dataset_root, f, output_folder, reses=[128,256,512,1024,2048], mode='square_crop') for f in json_src]

            print ("all jobs submitted!")

            for r in concurrent.futures.as_completed(futures):
                for country, base_name in r.result():

                    with open(os.path.join(output_folder, country + ".txt"), "a") as log:
                        log.write(base_name + "\n")
                        log.flush()

                    with open(os.path.join(output_folder, "all.txt"), "a") as log:
                        log.write(base_name + "\n")
                        log.flush()
    else:
        for f in json_src:
            render_labels_per_crop(dataset_root, f, output_folder, reses=[512], mode='square_crop')
