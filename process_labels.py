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


VALID_CROPS = {'square_crop', 'square_expand', 'none'}

colors = {}

PRETTY = 0
UGLY   = 1
GREY   = 2
PRETTY_FILMIC = 3
GREY_NO_DOOR = 4

COLOR_MODE = GREY

LABEL_SEQ = ["none","window pane","window frame",
             "open-window","wall frame","wall","door",
             "shutter","blind","bars","balcony","misc object",
             "roof", "door-pane"]

LABEL_SEQ_NO_DOOR = ["none", "window pane", "window frame",
                     "open-window", "wall frame", "wall",
                     "shutter", "blind", "bars", "balcony", "misc object"]

def colours_for_mode (mode):

    global PRETTY, UGLY, GREY
    colors = {}

    if mode == PRETTY: # pretty colors
        colors["none"]         = (255, 255, 255)
        colors["window pane"]  = (135, 170, 222)
        colors["window frame"] = (255, 128, 128)
        colors["open-window"]  = (0, 0, 0)
        colors["wall frame"]   = (233, 175, 198)
        colors["wall"]         = (231, 231, 231) # 231 on blossom + sash :/
        #colors["wall"]         = (204, 204, 204)
        colors["door"]         = (180, 151, 198)
        colors["shutter"]      = (255, 153,  85)
        colors["blind"]        = (255, 230, 128)
        colors["bars"]         = (90,   90,  90)
        colors["balcony"]      = (222, 170, 135)
        colors["misc object"]  = (174, 233, 174)
        colors["roof"]         = (167, 167, 167)
        colors["door-pane"]    = (124, 200, 185)

    if mode == PRETTY_FILMIC: # pretty colors if i forgot to set blender's color management view transform
        colors["none"]         = (255, 255, 255)
        colors["window pane"]  = (143, 168, 194)
        colors["window frame"] = (207, 137, 137)
        colors["open-window"]  = (0, 0, 0)
        colors["wall frame"]   = (199, 171, 183)
        colors["wall"]         = (166, 166, 166)
        colors["door"]         = (164, 120, 192)
        colors["shutter"]      = (207, 157, 96)
        colors["blind"]        = (255, 230, 128)
        colors["bars"]         = (110, 110, 110)
        colors["balcony"]      = (222, 170, 135)
        colors["misc object"]  = (174, 233, 174)
        colors["roof"]         = (166, 52, 61)
        colors["door-pane"]    = (112, 164, 174)

    elif mode == UGLY:
        colors["none"]         = (0, 0, 255)
        colors["window pane"]  = (0, 182, 206)
        colors["window frame"] = (206, 0, 0)
        colors["open-window"]  = (0, 0, 0)
        colors["wall frame"]   = (0, 158, 0)
        colors["wall"]         = (167, 167, 167)
        colors["door"]         = (164, 120, 192)
        colors["shutter"]      = (255, 153, 85)
        colors["blind"]        = (255, 230, 128)
        colors["bars"]         = (110, 110, 110)
        colors["balcony"]      = (222, 170, 135)
        colors["misc object"]  = (174, 233, 174)
        colors["roof"]         = (166, 52, 61)
        colors["door-pane"]    = (112, 164, 174)

    elif mode == GREY: # blender/label dataset greyscale colors
        colors["none"]         = (0)
        colors["window pane"]  = (1)
        colors["window frame"] = (2)
        colors["open-window"]  = (3)
        colors["wall frame"]   = (4)
        colors["wall"]         = (5)
        colors["door"]         = (6) # << remap door to window-frame
        colors["shutter"]      = (7)
        colors["blind"]        = (8)
        colors["bars"]         = (9)
        colors["balcony"]      = (10)
        colors["misc object"]  = (11)
        colors["roof"]         = (12)
        colors["door-pane"]    = (13)

    elif mode == GREY_NO_DOOR:  # blender/label dataset greyscale colors
        colors["none"]          = (0)
        colors["window pane"]   = (1)
        colors["window frame"]  = (2)
        colors["open-window"]   = (3)
        colors["wall frame"]    = (4)
        colors["wall"]          = (5)
        colors["door"]          = (2)  # << remap door to window-frame
        colors["shutter"]       = (6)
        colors["blind"]         = (7)
        colors["bars"]          = (8)
        colors["balcony"]       = (9)
        colors["misc object"]   = (10)
        colors["roof"]          = (0) # << render roof as none
        colors["door-pane"]     = (1) # << render door-window-pane as window-pane

    return colors

colors = colours_for_mode(COLOR_MODE)

def label_color_mode():
    global GREY, COLOR_MODE, GREY_NO_DOOR
    if COLOR_MODE == GREY or COLOR_MODE == GREY_NO_DOOR:
        return "L"
    else:
        return "RGBA"

def open_and_rotate(image_file, crop_data):

    if "dataset_root" in vars():
        photo = Image.open(os.path.join(dataset_root, "photos", image_file))
    else:
        photo = Image.open(image_file)

    if len(photo.getbands()) > 3:  # pngs..
        photo = photo.convert("RGB")

    # rotation usually encoded into photo...
    photo = ImageOps.exif_transpose(photo)

    # ...occasionally the crop tool allows defines a custom rotation
    rot = 0
    if "tags" in crop_data:
        for i, r in enumerate(["rot90", "rot180", "rot270"]):
            if r in crop_data["tags"]:
                rot = i + 1

    if rot > 0:
        photo = photo.transpose([Transpose.ROTATE_90, Transpose.ROTATE_180, Transpose.ROTATE_270][rot - 1])

    return photo

def render_labels_web (dataset_root, label_json_file, out_dir, flush_html = False, use_cache = False):

    colors = colours_for_mode(PRETTY)

    jp = Path(label_json_file)
    photo_name = os.path.splitext(jp.name)[0]
    labels_path = os.path.join(out_dir, photo_name + ".png")
    photo_path = os.path.join(out_dir, photo_name + ".with_labels.jpg")

    if use_cache and os.path.exists(labels_path) and os.path.exists(photo_path):
        return

    photo_file = find_photo_for_json(dataset_root, label_json_file)

    if os.stat(label_json_file).st_size == 0: # while the labelling is in progress, some label files are empty placeholders.
        print (f"skipping empty label file {label_json_file}")
        return

    with open(label_json_file, "r") as f:
        data = json.load(f)

    photo = open_and_rotate( os.path.join (dataset_root, "photos", photo_file ), data)
    draw_label_trans = ImageDraw.Draw(photo, 'RGBA')

    label_photo = Image.new("RGB", (photo.width, photo.height) )
    draw_label_photo = ImageDraw.Draw(label_photo, 'RGBA')
    draw_label_photo.rectangle([(0,0),(label_photo.width, label_photo.height)], fill=(255, 255, 255) )

    # crop to each defined region
    for crop_name, crop_data in data.items():
        crop_bounds = crop_data["crop"]
        if isinstance( crop_data["labels"], dict ): # labels part 1, render each category separately
            for cat, polies in crop_data["labels"].items():
                for poly in polies:
                    poly = [tuple(x) for x in poly]
                    poly = [ (crop_bounds[0] + a, crop_bounds[1] + b) for (a,b) in poly ]
                    draw_label_photo.polygon ( poly, colors[cat] )
                    draw_label_trans.polygon ( poly, (*colors[cat], 180), outline = (0,0,0), width=2 )
        else: # labels part 2, render overlapping labels in depth order
            for catl in crop_data["labels"]:
                cat=catl[0]
                for poly in catl[1]:
                    poly = [tuple(x) for x in poly]
                    poly = [ (crop_bounds[0] + a, crop_bounds[1] + b) for (a,b) in poly ]
                    draw_label_photo.polygon( poly, colors[cat])
                    draw_label_trans.polygon( poly, (* ( colors[cat]), 180), outline = (0,0,0), width=2 )

    print (f"saving labels to {labels_path} and transparents to {photo_path}")
    label_photo.save(labels_path, "PNG" )
    photo      .save( photo_path, "JPEG")

    if flush_html:
        # delete website resources/cache files to match...
        pfp = Path ( photo_file )
        batch = pfp.parent.name
        photo_root_name = os.path.splitext(pfp.name)[0]
        web_root = Path(dataset_root).joinpath(pfp.parent.parent.joinpath("metadata_website") )

        for to_del in [ web_root.joinpath("crops.html"),
                        web_root.joinpath("index.html"),
                        web_root.joinpath(batch).joinpath("html_index.html"),
                        web_root.joinpath(batch).joinpath("html_rects.html"),
                        web_root.joinpath(batch).joinpath(pfp.name),
                        web_root.joinpath(batch).joinpath(photo_root_name + ".html") ]:
            if os.path.exists(to_del):
                print(f"removing {to_del} cache file")
                os.remove(to_del)

def find_photo_for_json(dataset_root, json_file ):
    phop = Path(json_file)
    name = os.path.splitext(phop.name)[0]
    batch = phop.parent.name
    photo_file = os.path.join(dataset_root, "photos", batch, name + ".JPG")
    if not os.path.exists(photo_file):
        photo_file = os.path.join(dataset_root, "photos", batch, name + ".jpg")
    if not os.path.exists(photo_file):
        return None

    return photo_file


def crop( img, res=-1, mode='none', resample=None, background_col="black"):

    if resample == None:
        resample = Image.Resampling.BOX

    if mode == 'none':

        if res == -1:
            return img

        if img.width > img.height:
            img = img.resize((res, int(round(img.height * (res / img.width)))), resample=resample)
        else:
            img = img.resize((int(round(img.width * (res / img.height))), res), resample=resample)

        return img

    if mode == 'square_crop': # https://stackoverflow.com/questions/16646183/crop-an-image-in-the-centre-using-pil

        width  = img.size[0]
        height = img.size[1]

        new_width = min(width, height)

        left = int(np.ceil((width - new_width) / 2))
        right = width - np.floor((width - new_width) / 2)

        top = int(np.ceil((height - new_width) / 2))
        bottom = height - int(np.floor((height - new_width) / 2))

        img = img.crop ((left, top, right, bottom))

        if res != -1:
           img =  img.resize( (res, res), resample = resample)

        return img

    if mode == 'square_expand':

        width  = img.size[1]
        height = img.size[0]

        wh  = min(width, height)
        img = ImageOps.pad(img, (wh, wh), color=background_col)

        if res != -1:
           img =  img.resize( (res, res), resample = resample)

        return img

batch_to_country = None

def country_from_batch(dataset_root, batch_name):

    global batch_to_country

    if batch_to_country is None:
        batch_to_country = {}
        with open ( os.path.join(dataset_root, "metadata_location", "locations_data.json" ) ) as lf:
            locs = json.load( lf )
            for x in locs:
                batch_to_country[x["batch"]] = x["country"].lower()

    if batch_name in batch_to_country:
        return batch_to_country[batch_name]
    else:
        return "misc"

