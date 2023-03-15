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

def many_syn(rgbs, dataset_root, output_folder, folder_per_batch=False, res=512, mode='None', np_data=None):
    '''
    Render out labelled dataset
    '''

    random.shuffle(rgbs)
    os.makedirs(output_folder, exist_ok=True)
    svg_out = svgwrite.Drawing(os.path.join(output_folder, "labels.svg"), profile='tiny')

    xpos = -1
    ypos = 0

    colors = process_labels.colours_for_mode(process_labels.PRETTY)

    for rgb_file in rgbs:

        print (f"rendering crops from {rgb_file} @ {res}:{mode}")

        name = Path(rgb_file).with_suffix("").name

        label_file = Path(rgb_file).parent.parent.joinpath("labels").joinpath(Path(rgb_file).name )

        print(f" {xpos} -- {ypos} ")

        photo   = Image.open(rgb_file)
        if len(photo.getbands()) > 3:  # pngs..
            photo = photo.convert("RGB")
        label  = Image.open (label_file)

        row_h = 512
        scale = 0.1

        r = row_h / photo.height

        photo.save(os.path.join(output_folder, name + ".jpg"), format="JPEG")
        label.save(os.path.join(output_folder, name + ".png"), format="PNG")

        l_xpos = xpos + photo.width * scale
        ls = scale * r

        svg_out.add(svg_out.image(href=name+".jpg", insert=(xpos, ypos), size=(photo.width * scale, photo.height * scale)))
        svg_out.add(svg_out.image(href=name + ".png", insert=(l_xpos, ypos), size=(photo.width * scale, photo.height * scale)))

        svg_out.add(svg_out.rect(
            (l_xpos, ypos),
            (photo.width * scale, photo.height * scale),
            fill='none', stroke='black', stroke_width=0.5
        ) )

        pad = 5
        xpos += photo.width * scale * 2 + pad
        if xpos >= 600:
            xpos = 0
            ypos += row_h * scale + pad

        if ypos > 3000:
            svg_out.save()
            return

    svg_out.save()

if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Downloads\snow_200"
        output_folder = r"C:\Users\twak\Downloads\ad_syn"
    else:
        dataset_root = r"/home/kellyt/is/windowz/winsyn_snow"
        output_folder = r"/home/kellyt"

    os.makedirs(output_folder, exist_ok=True)

    rgbs = []
    rgbs.extend (glob.glob(os.path.join(dataset_root, "rgb", "*.png")))

    np_data = None  # []

    many_syn(rgbs, dataset_root, output_folder, folder_per_batch=False, res=-1, mode='none', np_data=np_data)

