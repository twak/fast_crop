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

def render_labels_per_crop( json_files, dataset_root, output_folder, folder_per_batch=False, res=512, mode='None', np_data=None):
    '''
    Render out labelled dataset
    '''

    random.shuffle(json_files)
    os.makedirs(output_folder, exist_ok=True)
    svg_out = svgwrite.Drawing(os.path.join(output_folder, "labels.svg"), profile='tiny')

    xpos = -1
    ypos = 0

    colors = process_labels.colours_for_mode(process_labels.PRETTY)

    for json_file in json_files:

        print (f"rendering crops from {json_file} @ {res}:{mode}")
        batch_name = Path(json_file).parent.name



        photo_file = process_labels.find_photo_for_json(dataset_root, json_file )

        batch_name = Path(json_file).parent.name

        with open(json_file, "r") as f:
            data = json.load(f)



        # crop to each defined region
        for crop_name, crop_data in data.items():

            print(f" {xpos} -- {ypos} ")


            crop_bounds = crop_data["crop"]
            photo_l = process_labels.open_and_rotate(os.path.join(dataset_root, photo_file), data)
            photo_l  = photo_l.crop (crop_bounds)

            row_h = 800
            scale = 0.1

            r = row_h / photo_l.height
            photo = photo_l.resize((int(photo_l.width * r), int(row_h)), resample=Image.Resampling.BOX)
            s_im_name = f"{batch_name}_{Path(photo_file).name}.jpg"
            photo.save(os.path.join(output_folder, s_im_name), format="JPEG")

            l_xpos = xpos + photo.width * scale
            ls = scale * r

            svg_out.add(svg_out.image(href=s_im_name, insert=(xpos, ypos), size=(photo.width * scale, photo.height * scale)))

            for cat, polies in crop_data["labels"].items():

                for poly in polies:
                    poly = [tuple((x[0] * ls + l_xpos, x[1] * ls + ypos)) for x in poly]
                    svg_out.add(svg_out.polygon(poly, fill=f'rgb({colors[cat][0]},{colors[cat][1]},{colors[cat][2]})'))

            svg_out.add(svg_out.rect(
                (l_xpos, ypos),
                (photo.width * scale, photo.height * scale),
                fill='none', stroke='black', stroke_width=0.5
            ) )

            break # just do first crop..

        pad = 5
        xpos += photo.width * scale * 2 + pad
        if xpos >= 800:
            xpos = 0
            ypos += row_h * scale + pad

        if ypos > 1200:
            svg_out.save()
            return

if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"E:\dataset"
        output_folder = r"C:\Users\twak\Downloads\ad_labels"
    else:
        dataset_root = r"/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"
        output_folder = r"/datawaha/cggroup/kellyt/iccv_add_mat/labels"

    os.makedirs(output_folder, exist_ok=True)

    json_src = []
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

    np_data = None  # []

    render_labels_per_crop(json_src, dataset_root, output_folder, folder_per_batch=False, res=-1, mode='none', np_data=np_data)
