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
import random

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


def grid_o_crops(name, images, output_dir, quality=98):
    '''
    creates svg with many crops of images
    '''

    os.makedirs(output_dir, exist_ok=True)
    name_map = {}

    fm = 'w'
    log = open( os.path.join ( output_dir, 'log.txt'), fm)

    svg_out = svgwrite.Drawing(os.path.join(output_folder, name+".svg"), profile='tiny')

    random.shuffle(images)

    min_dim = 512

    print (f"found {len(images)} jpgs")

    xpos_l = -1
    ypos_l = 0

    xpos_p = -1
    ypos_p = 0

    for im_file in images:

        print ('processing %s...' % im_file)

        out_name, out_ext = os.path.splitext ( os.path.basename(im_file) )
        out_ext = out_ext.lower()

        batch_name = Path(im_file).parent.name

        json_file = Path(im_file).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch_name).joinpath(f"{out_name}.json")

        if os.path.exists(os.path.join (".",json_file ) ): # crop

            prev = json.load(open(json_file, "r") )
            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            size = 60
            max_x = 10
            max_y = 10

            im_l = process_labels.open_and_rotate( im_file, prev )
            im = crop(im_l, 600, 'none')

            s_im_name = Path(im_file).name
            im.save(os.path.join(output_dir, s_im_name), format="JPEG" )

            if im.width > im.height: # landscape

                width = size
                height = int(round(im.height * (size / im.width)))

                xpos_l += 1
                if xpos_l >= max_x:
                    xpos_l = 0
                    ypos_l += 1

                xoff = xpos_l * size + (size - width) / 2  # , ypos * size + yoff
                yoff = ypos_l * height + (size - height) / 2

            else: # portrait
                width = int(round(im.width * (size / im.height)))
                height = size

                xpos_p += 1
                if xpos_p >= max_x * 1.6: # more portrait ones pls...
                    xpos_p = 0
                    ypos_p += 1

                xoff = size *(max_x+1) + xpos_p * width + (size - width) / 2  # , ypos * size + yoff
                yoff = ypos_p * size + (size - height) / 2

            print ( f" max col {ypos_l} {ypos_p}")

            if ypos_l > max_y or ypos_p > max_y:
                break

            svg_out.add(svg_out.image(href=s_im_name, insert=(xoff, yoff), size=(width, height) ) )

            for r in rects:

                if not ( "window" in r[1] or "glass_facade" in r[1] or "shop" in r[1] or "church" in r[1] or "abnormal" in r[1] ):
                    continue

                c = r[0]

                if c[2] - c[0] < min_dim or c[3] - c[1] < min_dim:
                    print("skipping small rect")
                    continue

                svg_out.add(svg_out.rect((
                    ( c[0] * width / im_l.width + xoff ),
                    ( c[1] * height / im_l.height + yoff )               ), (
                    (c[2]-c[0]) * width / im_l.width,
                    (c[3]-c[1]) * height / im_l.height),
                    fill='none', stroke=svgwrite.rgb(255, 128, 128), stroke_width=0.5 ) ) # fill=colors["none"])

        else:
            print("no metadata_single_element crop file, skipping")

    svg_out.save()
    log.close()


VALID_CROPS = {'square_crop', 'square_expand', 'none'}


if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Downloads\ambleside_tolabel"
    else:
        dataset_root = "."
        # dataset_root = r"/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"

    #output_folder = r"/datawaha/cggroup/kellyt/iccv_add_mat/photos"  # f"./metadata_single_elements/dataset_cook{time.time()}
    output_folder = "/home/twak/fig_crops/" # r"C:\Users\twak\Downloads\iccv_fig_tmp"  # f"./metadata_single_elements/dataset_cook{time.time()}

    os.makedirs(output_folder, exist_ok=True)

    photo_src = []
    # photo_src.extend(glob.glob(r'./photos/tom_ambleside_20230101/*.JPG'))

    for name, batches in [("uk", [ "tom_ambleside_20230101", "tom_bramley_20220406", "tom_cams_20220418", "tom_dales_20220403",
            "tom_leeds_docks_20220404", "tom_london_20220418", "tom_saffron_20220418", "tom_york_20220411" ] ),

                          ("usa", ["brian_la_20220905", "kaitlyn_ny_20221205", "kalinia_la_20230128", "nicklaus_miami_20230301",
            "peter_washington_20221129", "scarlette_chicago_20221022"] ),

                        ("aus", ["michaela_vienna_20220425",     "michaela_vienna_20220426",     "michaela_vienna_20220427",     "michaela_vienna_20220428",
    "michaela_vienna_20220429",    "michaela_vienna_20220502",     "michaela_vienna_20220503",     "michaela_vienna_20220603",
    "michaela_vienna_20220608",     "michaela_vienna_20220609",    "michaela_vienna_20220611",    "michaela_vienna_20220614",
    "michaela_vienna_20220615",    "michaela_vienna_20220617",    "michaela_vienna_20220618",    "michaela_vienna_20220628",
    "michaela_vienna_20220629",    "michaela_vienna_20220704",    "michaela_vienna_20220705",    "michaela_vienna_20220706",
    "michaela_vienna_20220707",    "michaela_vienna_20220712",    "michaela_vienna_20220713",    "michaela_vienna_20220714"]),

                          ("ger", ["michaela_berlin_20221000", "michaela_berlin_20221018", "michaela_berlin_20221019", "michaela_berlin_20221020",
    "michaela_berlin_20221021", "michaela_berlin_20221024", "michaela_berlin_20221025", "michaela_berlin_20221026",
    "michaela_berlin_20221027", "michaela_berlin_20221028"]),
                          ]:
        for batch in batches:
            photo_src.extend(glob.glob( os.path.join(dataset_root, "photos", batch, "*.JPG" )) )
        grid_o_crops(name, photo_src, output_folder, quality=80)



    # for batch in :

