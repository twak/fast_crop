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

colors = {}

PRETTY = 0
UGLY   = 1
GREY   = 2
PRETTY_FILMIC = 3

COLOR_MODE = GREY
LABEL_SEQ = ["none","window pane","window frame","open-window","wall frame","wall","door","shutter","blind","bars","balcony","misc object"]

def colours_for_mode (mode):

    global PRETTY, UGLY, GREY
    colors = {}

    if mode == PRETTY: # pretty colors
        colors["none"]         = (255, 255, 255)
        colors["window pane"]  = (135, 170, 222)
        colors["window frame"] = (255, 128, 128)
        colors["open-window"]  = (0, 0, 0)
        colors["wall frame"]   = (233, 175, 198)
        colors["wall"]         = (204, 204, 204)
        colors["door"]         = (164, 120, 192)
        colors["shutter"]      = (255, 153, 85)
        colors["blind"]        = (255, 230, 128)
        colors["bars"]         = (110, 110, 110)
        colors["balcony"]      = (222, 170, 135)
        colors["misc object"]  = (174, 233, 174)
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
    elif mode == UGLY: # blender/label dataset colors
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
    elif mode == GREY: # blender/label dataset colors
        colors["none"]         = (0)
        colors["window pane"]  = (1)
        colors["window frame"] = (2)
        colors["open-window"]  = (3)
        colors["wall frame"]   = (4)
        colors["wall"]         = (5)
        colors["door"]         = (6)
        colors["shutter"]      = (7)
        colors["blind"]        = (8)
        colors["bars"]         = (9)
        colors["balcony"]      = (10)
        colors["misc object"]  = (11)

    return colors

colors = colours_for_mode(COLOR_MODE)

def label_color_mode():
    global GREY, COLOR_MODE
    if COLOR_MODE == GREY:
        return "L"
    else:
        return "RGBA"

def render_labels_web (dataset_root, label_json_file, flush_html = False, use_cache = False):

    global colors

    jp = Path(label_json_file)
    photo_name = os.path.splitext(jp.name)[0]
    labels_path = os.path.join(jp.parent, photo_name + ".png")
    photo_path = os.path.join(jp.parent, photo_name + ".jpg")

    if use_cache and os.path.exists(labels_path) and os.path.exists(photo_path):
        return

    photo_file = find_photo_for_json(dataset_root, label_json_file)

    # read src input
    photo = Image.open(os.path.join (dataset_root, "photos", photo_file ))
    photo = ImageOps.exif_transpose(photo)
    draw_label_trans = ImageDraw.Draw(photo, 'RGBA')

    with open(label_json_file, "r") as f:
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
        resample = Image.Resampling.BOXs

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



def render_labels_per_crop( dataset_root, json_file, output_folder, folder_per_batch=False, res=512, mode='None', np_data=None):
    '''
    Render out labelled dataset
    '''

    print (f"rendering crops from {json_file} @ {res}:{mode}")

    global colors

    photo_file = find_photo_for_json(dataset_root, json_file )

    os.makedirs(os.path.join(output_folder, "rgb"   ), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)

    # read src input
    photo = Image.open(os.path.join(dataset_root, photo_file))
    photo = ImageOps.exif_transpose(photo)

    batch_name = Path(json_file).parent.name

    with open(json_file, "r") as f:
        data = json.load(f)

    label_mode = label_color_mode()

    # crop to each defined region
    for crop_name, crop_data in data.items():

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
        crop_photo = crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
        label_img  = crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")

        base_name = os.path.splitext(crop_name)[0]

        if folder_per_batch: # split by country

            if "tom_" in batch_name:
                country = "england"
            elif "michaela_" in batch_name:
                country = "austria"
            else:
                country = None

            if country is not None:
                country_loc = os.path.join(output_folder, country)

                os.makedirs(os.path.join(country_loc, "rgb"), exist_ok=True)
                os.makedirs(os.path.join(country_loc, "labels"), exist_ok=True)

                crop_photo.save(os.path.join(country_loc, "rgb", base_name + ".jpg"))
                label_img.save (os.path.join(country_loc, "labels", base_name + ".png"))

            # base_name = os.path.join ( batch_name, base_name )
            # os.makedirs(os.path.join(output_folder, "rgb", batch_name), exist_ok=True)
            # os.makedirs(os.path.join(output_folder, "labels", batch_name), exist_ok=True)

        crop_photo.save(os.path.join(output_folder, "rgb"   , base_name + ".jpg"))
        label_img .save(os.path.join(output_folder, "labels", base_name + ".png"))

        if np_data is not None:
            np_data.append( np.asarray(crop_photo) )



def render_metadata_single(images, output_dir, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution=512, quality=98):
    '''
    renders all each crop to a uniquely named file
    '''

    global VALID_CROPS

    os.makedirs(output_dir, exist_ok=True)
    name_map = {}

    fm = 'w' if clear_log else 'a'
    log = open( os.path.join ( output_dir, 'log.txt'), fm)

    def save(im, out_name):

        if len (im.getbands() ) > 3: # pngs..
             im = im.convert("RGB")

        if im.width == 0 or im.height == 0:
            print("skipping zero sized rect in %s" % out_name)
            return

        md5hash = hashlib.md5(im.tobytes())
        jpg_out_file = "%s.jpg" % md5hash.hexdigest()
        log.write("\"%s\"\n" % jpg_out_file)


        out_path = os.path.join(output_dir, jpg_out_file)

        im.save(out_path, format="JPEG", quality=quality)

    if not crop_mode in VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(VALID_CROPS)))
        return

    min_dim = 2048 # 1024 lost 77/3,100 at this resolution (12.4.22)
    count = 0

    print (f"found {len(images)} jpgs")

    for im_file in images:

        if sub_dirs:
            sub_dir = os.path.split ( os.path.split(im_file)[0] )[1]
            dir = os.path.join(output_dir, sub_dir)
            os.makedirs( dir, exist_ok=True)

        print ('processing %s...' % im_file)

        out_name, out_ext = os.path.splitext ( os.path.basename(im_file) )
        out_ext = out_ext.lower()

        batch = Path(im_file).parent.name
        json_file = Path(im_file).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch).joinpath(f"{out_name}.json")

        if os.path.exists(os.path.join (".",json_file ) ): # crop

            im = ImageOps.exif_transpose(Image.open(im_file))

            prev = json.load(open(json_file, "r") )
            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            for r in rects:

                if not ( "window" in r[1] or "glass_facade" in r[1] or "shop" in r[1] or "church" in r[1] or "abnormal" in r[1] ):
                    continue

                r = r[0]

                if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
                    print("skipping small rect")
                    continue

                log.write("%s [%d, %d, %d, %d]\n" % (im_file, r[0], r[1], r[2], r[3]) )

                crop_im = im.crop( ( r[0], r[1], r[2], r[3] ) )
                crop_im = crop(crop_im, resolution, crop_mode)

                save(crop_im, out_name)
                count = count + 1

                print(f"count {count}")

        else:
            print("no metadata_single_element crop file, skipping")

    log.close()


VALID_CROPS = {'square_crop', 'square_expand', 'none'}


if __name__ == "__main__":


    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
    else:
        dataset_root = r"/mnt/vision/data/archinet/data"

    output_folder = r"C:\Users\twak\Downloads\tuesday_debug"

    # render single-windows crops
    # cut_n_shut(...)

    json_src = []
    #json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

    # json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "tom_archive_19000102", "*.json")))
    # json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_batch_1_fixed_24.06.2022\**.json'))
    # render labels over whole photos for the website

    # photos = []
    # photos.extend(glob.glob(os.path.join(dataset_root, "photos", "*", "*.JPG")))
    # photos.extend(glob.glob(os.path.join(dataset_root, "photos", "*", "*.jpg")))

    np_data = []

    for f in json_src:
        render_labels_per_crop( dataset_root, f, output_folder, folder_per_batch=True, res=512, mode='square_crop', np_data=np_data)

    all_data = np.concatenate(tuple(np_data), 0)
    print(f"mean [{np.mean(all_data, axis=(0,1))}] std [{np.std(all_data, axis=(0,1))}]")

    # generate dataset from all metadata_single_element
    # photo_src = []
    # photo_src.extend(glob.glob(r'./photos/*/*.JPG'))
    # photo_src.extend(glob.glob(r'./photos/*/*.jpg'))
    # cut_n_shut(photo_src, f"./metadata_single_elements/dataset_cook{time.time()}", crop_mode="square_crop", resolution=1024, quality=95, sub_dirs=False )