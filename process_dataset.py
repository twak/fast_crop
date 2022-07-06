import copy
import glob
import hashlib
import json

# from the index file when we created the crops for the labellers to our src coordinate system
import os
import random
from collections import defaultdict
from os import path
from pathlib import Path
import PIL
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
from PIL import ImageOps
import numpy as np

colors = {}

if False: # pretty colors
    colors["window pane"] = (135, 170, 222)
    colors["window frame"] = (255, 128, 128)
    colors["open-window"] = (0, 0, 0)
    colors["wall frame"] = (233, 175, 198)
    colors["wall"] = (204, 204, 204),
    colors["door"] = (164, 120, 192)
    colors["shutter"] = (255, 153, 85)
    colors["blind"] = (255, 230, 128)
    colors["bars"] = (110, 110, 110)
    colors["balcony"] = (222, 170, 135)
    colors["misc object"] = (174, 233, 174)

else: # blender colors

    colors["window pane"] = (0, 182, 206)
    colors["window frame"] = (206, 0, 0)
    colors["open-window"] = (0, 0, 0)
    colors["wall frame"] = (0, 158, 0)
    colors["wall"] = (167, 167, 167)
    colors["door"] = (164, 120, 192)
    colors["shutter"] = (255, 153, 85)
    colors["blind"] = (255, 230, 128)
    colors["bars"] = (110, 110, 110)
    colors["balcony"] = (222, 170, 135)
    colors["misc object"] = (174, 233, 174)

def render_labels_web (dataset_root, json_file):

    global colors

    photo_file = find_photo_for_json(dataset_root, json_file)

    # read src input
    photo = Image.open(os.path.join (dataset_root, "photos", photo_file ))
    photo = ImageOps.exif_transpose(photo)
    draw_label_trans = ImageDraw.Draw(photo, 'RGBA')

    with open(json_file, "r") as f:
        data = json.load(f)

    label_photo = Image.new("RGB", (photo.width, photo.height) )
    draw_label_photo = ImageDraw.Draw(label_photo, 'RGBA')
    draw_label_photo.rectangle([(0,0),(label_photo.width, label_photo.height)], fill=(255, 255, 255) )

    # crop to each defined region
    for crop_name, crop_data in data.items():

        crop_bounds = crop_data["crop"]

        # label_crop = Image.new("RGB", (crop_bounds[2] - crop_bounds[0], crop_bounds[3] - crop_bounds[1]))
        # draw = ImageDraw.Draw(label_crop)

        for cat, polies in crop_data["labels"].items():
            for poly in polies:

                poly = [tuple(x) for x in poly]

                # draw.polygon(poly, colors[cat] ) #random.randrange(0,255))

                poly = [ (crop_bounds[0] + a, crop_bounds[1] + b) for (a,b) in poly ]

                # for idx, pt in poly:
                #     poly[idx] = (crop_bounds[0] + pt[0], crop_bounds[1] + pt[1])

                draw_label_photo.polygon ( poly, colors[cat] )
                draw_label_trans.polygon ( poly, (*colors[cat], 180), outline = (0,0,0) )

    jp = Path(json_file)
    label_photo.save(os.path.join(jp.parent, os.path.splitext(jp.name)[0] + ".png"), "PNG")
    photo.save(os.path.join(jp.parent, os.path.splitext(jp.name)[0] + ".jpg"), "JPEG")

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


def render_per_crop( dataset_root, json_file, output_folder, res=512, mode='None'):

    print (f"rendering crops from {json_file} @ {res}:{mode}")

    global colors

    photo_file = find_photo_for_json(dataset_root, json_file )

    os.makedirs(os.path.join(output_folder, "rgb"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)

    # read src input
    photo = Image.open(os.path.join(dataset_root, photo_file))
    photo = ImageOps.exif_transpose(photo)

    with open(json_file, "r") as f:
        data = json.load(f)

    # crop to each defined region
    for crop_name, crop_data in data.items():

        crop_bounds = crop_data["crop"]
        crop_photo =photo.crop (crop_bounds)

        label_img = Image.new("RGB", (crop_photo.width, crop_photo.height))
        draw_label_photo = ImageDraw.Draw(label_img, 'RGBA')
        draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=(255, 255, 255))

        for cat, polies in crop_data["labels"].items():

            for poly in polies:
                poly = [tuple(x) for x in poly]
                draw_label_photo.polygon(poly, colors[cat])

        crop_photo = crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
        label_img  = crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")

        crop_name = os.path.splitext(crop_name)[0]
        crop_photo.save(os.path.join(output_folder, "rgb"   , crop_name + ".jpg"))
        label_img .save(os.path.join(output_folder, "labels", crop_name + ".png"))


def find_photo_for_json(dataset_root, json_file ):
    phop = Path(json_file)
    name = os.path.splitext(phop.name)[0]
    batch = phop.parent.name
    photo_file = os.path.join(dataset_root, "photos", batch, name + ".jpg")
    if not os.path.exists(photo_file):
        photo_file = os.path.join(dataset_root, "photos", batch, name + ".JPG")
    return photo_file


def crop( img, res=-1, mode='none', resample=Image.Resampling.BOX, background_col="black"):

    if mode == 'none':
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


def cut_n_shut(images, dir_, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution=512, quality=98):

    global VALID_CROPS

    os.makedirs(dir_, exist_ok=True)
    dir = dir_
    name_map = {}

    fm = 'w' if clear_log else 'a'
    log = open( os.path.join ( dir_, 'log.txt'), fm)

    def save(im, out_name):

        if len (im.getbands() ) > 3: # pngs..
             im = im.convert("RGB")

        if im.width == 0 or im.height == 0:
            print("skipping zero sized rect in %s" % out_name)
            return

        md5hash = hashlib.md5(im.tobytes())
        jpg_out_file = "%s.jpg" % md5hash.hexdigest()
        # name_map[md5hash] =
        log.write("\"%s\"\n" % jpg_out_file)


        out_path = os.path.join(dir, jpg_out_file)

        im.save(out_path, format="JPEG", quality=quality)

    if not crop_mode in VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(VALID_CROPS)))
        return

    # resolution = 512
#        mode = 'square_crop'
#         crop_mode = 'square_expand'
#         crop_mode = 'none'
    min_dim = 2048 # 1024 lost 77/3,100 at this resolution (12.4.22)

    for im_file in images:

        if sub_dirs:
            sub_dir = os.path.split ( os.path.split(im_file)[0] )[1]
            dir = os.path.join(dir_, sub_dir)
            os.makedirs( dir, exist_ok=True)

        print ('processing %s...' % im_file)

        im = ImageOps.exif_transpose(Image.open(im_file))

        out_name, out_ext = os.path.splitext ( os.path.basename(im_file) )
        out_ext = out_ext.lower()

        pre, ext = os.path.splitext(im_file)
        json_file = pre + ".json"

        count = 0

        if os.path.exists(json_file): # crop
            prev = json.load(open(json_file, "r"))
            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            for r in rects:

                if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
                    print("skipping small rect")
                    continue

                log.write("%s [%d, %d, %d, %d]\n" % (im_file, r[0], r[1], r[2], r[3]) )

                crop_im = im.crop( ( r[0], r[1], r[2], r[3] ) )
                crop_im = crop(crop_im, resolution, crop_mode)

                save(crop_im, out_name)
                count = count + 1
        else: # whole image
            im = crop(im, resolution, crop_mode)
            log.write(im_file + f"[0,0,{im.width},{im.height}]\n")
            save ( im, out_name )

    log.close()


VALID_CROPS = {'square_crop', 'square_expand', 'none'}

dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
output_folder = r"C:\Users\twak\Downloads\rendered_dataset"

# render single-windows crops
# cut_n_shut(...)

json_src = []
#json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
json_src.extend(glob.glob( os.path.join (dataset_root, "metadata_window_labels", "*", "*.json" ) ) ) # r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_batch_1_fixed_24.06.2022\**.json'))

# render labels over whole photos for the website
# for j in json_src:
#     render_labels_web( dataset_root, j)

# for all crops that have labels in metadata_window_labels

for f in json_src:
    render_per_crop( dataset_root, f, output_folder, res=512, mode='square_crop')