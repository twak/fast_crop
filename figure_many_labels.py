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

    max_x = 5
    max_y = 10

    for json_file in json_files:

        print (f"rendering crops from {json_file} @ {res}:{mode}")



        batch_name = Path(json_file).parent.name

        # if not "tom_" in batch_name and not "michaela_" in batch_name:
        #     return
        #
        # if "archive" in batch_name or "copenhagen" in batch_name:
        #     return

        global colors

        photo_file = process_labels.find_photo_for_json(dataset_root, json_file )

        batch_name = Path(json_file).parent.name

        with open(json_file, "r") as f:
            data = json.load(f)

        photo =  process_labels.open_and_rotate( os.path.join(dataset_root, photo_file), data )

        label_mode =  process_labels.label_color_mode()

        # crop to each defined region
        for crop_name, crop_data in data.items():

            xpos += 1
            if xpos >= max_x:
                xpos = 0
                ypos += 1

            if ypos > max_y:
                svg_out.save()
                return

            crop_bounds = crop_data["crop"]
            crop_photo =photo.crop (crop_bounds)

            label_img = Image.new(label_mode, (crop_photo.width, crop_photo.height))
            draw_label_photo = ImageDraw.Draw(label_img, label_mode)
            draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=colors["none"] )

            for cat, polies in crop_data["labels"].items():

                for poly in polies:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon( poly, colors[cat])

            # crop down
            crop_photo = process_labels.crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
            label_img  = process_labels.crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")

            base_name = os.path.splitext(crop_name)[0]

            crop_photo.save(os.path.join(output_folder, "rgb"   , base_name + ".jpg"))
            label_img .save(os.path.join(output_folder, "labels", base_name + ".png"))


            if True: # svg

                label_img = Image.new(label_mode, (crop_photo.width, crop_photo.height))
                draw_label_photo = ImageDraw.Draw(label_img, label_mode)
                draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=colors["none"])
                dwg = svgwrite.Drawing(os.path.join(output_folder, "svg", crop_name + ".svg"), profile='tiny')
                dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
                dwg.add(dwg.text(crop_name, insert=(0, 0.2), fill='black'))

                for cat, polies in crop_data["labels"].items():
                # for catl in crop_data["labels"]:

                    # cat = catl[0]

                    for poly in polies:
                        poly = [tuple(x) for x in poly]
                        draw_label_photo.polygon(poly, colors[cat])
                        dwg.add(dwg.polygon(poly, fill=f'rgb({colors[cat][0]},{colors[cat][1]},{colors[cat][2]})'))

                dwg.save()

            if np_data is not None:
                np_data.append( np.asarray(crop_photo) )




VALID_CROPS = {'square_crop', 'square_expand', 'none'}


if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
    else:
        dataset_root = r"/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"

    output_folder = r"/datawaha/cggroup/kellyt/iccv_add_mat/photos" #f"./metadata_single_elements/dataset_cook{time.time()}

    os.makedirs(output_folder, exist_ok=True)

    json_src = []
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

    np_data = None  # []

    render_labels_per_crop(json_src, dataset_root, output_folder, folder_per_batch=False, res=-1, mode='none', np_data=np_data)

    if np_data is not None:
        all_data = np.concatenate(tuple(np_data), 0)
        print(f"mean [{np.mean(all_data, axis=(0,1))}] std [{np.std(all_data, axis=(0,1))}]")
