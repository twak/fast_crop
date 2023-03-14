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


def grid_o_crops(images, output_dir, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution=512, quality=98):
    '''
    creates svg with many crops of images
    '''

    os.makedirs(output_dir, exist_ok=True)
    name_map = {}

    fm = 'w' if clear_log else 'a'
    log = open( os.path.join ( output_dir, 'log.txt'), fm)

    svg_out = svgwrite.Drawing(os.path.join(output_folder, "many.svg"), profile='tiny')
    # dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
    # dwg.add(dwg.text(crop_name, insert=(0, 0.2), fill='black'))

    random.shuffle(images)

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

    if not crop_mode in VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(VALID_CROPS)))
        return

    min_dim = 512
    count = 0

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

        if sub_dirs:
            # sub_dir = os.path.split ( os.path.split(im_file)[0] )[1]
            dir = os.path.join(output_dir, batch_name)
            os.makedirs( dir, exist_ok=True)


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
    output_folder = "~/uk_crops/" # r"C:\Users\twak\Downloads\iccv_fig_tmp"  # f"./metadata_single_elements/dataset_cook{time.time()}

    os.makedirs(output_folder, exist_ok=True)

    photo_src = []
    # photo_src.extend(glob.glob(r'./photos/tom_ambleside_20230101/*.JPG'))

    for batch in [ "tom_ambleside_20230101", "tom_bramley_20220406", "tom_cams_20220418", "tom_dales_20220403",
            "tom_leeds_docks_20220404", "tom_london_20220418", "tom_saffron_20220418", "tom_york_20220411" ]:
        photo_src.extend(glob.glob( os.path.join(dataset_root, "photos", batch, "*.JPG" )) )

    grid_o_crops(photo_src, output_folder, crop_mode="square_crop", resolution=512, quality=80, sub_dirs=True)