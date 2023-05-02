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

colors = {}

PRETTY = 0
UGLY   = 1
GREY   = 2
PRETTY_FILMIC = 3

COLOR_MODE = PRETTY
LABEL_SEQ = ["none","window pane","window frame","open-window","wall frame","wall","door","shutter","blind","bars","balcony","misc object", "roof", "door-pane"]

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
        colors["door-pane"] = (112, 164, 174)
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
        colors["door-pane"] = (112, 164, 174)
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
        # colors["roof"]         = (12)
        # colors["door-pane"]    = (13)

    return colors

colors = colours_for_mode(COLOR_MODE)

def label_color_mode():
    global GREY, COLOR_MODE
    if COLOR_MODE == GREY:
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

def country_from_batch(batch_name):

    if "tom_" in batch_name and "copenhagen" not in batch_name and "thuwal" not in batch_name:
        return "uk"
    elif "michaela_vienna" in batch_name:
        return "austria"
    elif "michaela_berlin" in batch_name:
        return "germany"
    elif "brian_la_20220905" in batch_name or "scarlette_chicago_20221022" in batch_name or "peter_washington_20221129" in batch_name or "kaitlyn_ny_20221205" in batch_name or "samantha_newyork_20230313" in batch_name or "nicklaus_miami_20230301" in batch_name or "kalinia_la_20230128" in batch_name:
        return "usa"
    elif "elsayed_" in batch_name:
        return "egypt"
    else:
        return "other"

def render_labels_per_crop( dataset_root, json_file, output_folder, folder_per_batch=False, res=512, mode='None', np_data=None):
    '''
    Render out labelled dataset
    '''

    print (f"rendering crops from {json_file} @ {res}:{mode}")

    global colors

    photo_file = find_photo_for_json(dataset_root, json_file )

    os.makedirs(os.path.join(output_folder, "rgb"   ), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "svg"), exist_ok=True)

    batch_name = Path(json_file).parent.name

    country = country_from_batch(batch_name)

    if  os.stat(json_file).st_size == 0: # while the labelling is in progress, some label files are empty placeholders.
        print ("skipping empty label file")
        return

    with open(json_file, "r") as f:
        data = json.load(f)

    photo = open_and_rotate( os.path.join(dataset_root, photo_file), data )

    label_mode = label_color_mode()

    # crop to each defined region
    for crop_name, crop_data in data.items():

        crop_bounds = crop_data["crop"]
        crop_photo =photo.crop (crop_bounds)

        label_img = Image.new(label_mode, (crop_photo.width, crop_photo.height))
        draw_label_photo = ImageDraw.Draw(label_img, label_mode)
        draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=colors["none"] )

        if isinstance( crop_data["labels"], dict ): # labels part 1, render each category separately
            for cat, polies in crop_data["labels"].items():
                for poly in polies:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon( poly, colors[cat])
        else: # labels part 2, render in order
            for catl in crop_data["labels"]:
                cat = catl[0]
                for poly in catl[1]:
                    poly = [tuple(x) for x in poly]
                    draw_label_photo.polygon(poly, colors[cat])

        # crop down
        crop_photo = crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
        label_img  = crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")

        base_name = os.path.splitext(crop_name)[0]

        # base_name = base_name.replace("_new", "") # patch names sent to labellers
        # base_name = base_name.replace("IMG_0276", hashlib.md5(crop_photo.tobytes()).hexdigest() )

        # if folder_per_batch: # split by country
        #
        #
        #     if country is not None:
        #         country_loc = os.path.join(output_folder, country)
        #
        #         os.makedirs(os.path.join(country_loc, "rgb"), exist_ok=True)
        #         os.makedirs(os.path.join(country_loc, "labels"), exist_ok=True)
        #
        #         crop_photo.save(os.path.join(country_loc, "rgb", base_name + ".png"))
        #         label_img.save (os.path.join(country_loc, "labels", base_name + ".png"))
        #
        #     # base_name = os.path.join ( batch_name, base_name )
        #     # os.makedirs(os.path.join(output_folder, "rgb", batch_name), exist_ok=True)
        #     # os.makedirs(os.path.join(output_folder, "labels", batch_name), exist_ok=True)

        crop_photo.save(os.path.join(output_folder, "rgb"   , base_name + ".jpg"))
        label_img .save(os.path.join(output_folder, "labels", base_name + ".png"))

        with open ( os.path.join (output_folder, country+".txt"), "a" ) as log:
            log.write(base_name+"\n")
            log.flush()

        with open ( os.path.join (output_folder, "all.txt"), "a" ) as log:
            log.write(base_name+"\n")
            log.flush()


        if False: # svg

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



def render_crops(images, output_dir, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution=512, quality=98):
    '''
    renders all crops to a uniquely named file
    '''

    global VALID_CROPS

    os.makedirs(output_dir, exist_ok=True)
    name_map = {}

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

    if not crop_mode in VALID_CROPS:
        print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(VALID_CROPS)))
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

        # if not "tom_" in batch_name and not "michaela_" in batch_name:
        #     continue
        #
        # if "archive" in batch_name or "copenhagen" in batch_name or "thuwal" in batch_name:
        #     continue

        json_file = Path(im_file).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch_name).joinpath(f"{out_name}.json")

        if os.path.exists(os.path.join (".",json_file ) ): # crop

            prev = json.load(open(json_file, "r") )
            im = open_and_rotate( im_file, prev )
            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            for r in rects:

                if not ( "window" in r[1] or "door" in r[1] or "glass_facade" in r[1] or "shop" in r[1] or "church" in r[1] or "abnormal" in r[1] ):
                    continue

                c = r[0]

                if c[2] - c[0] < min_dim or c[3] - c[1] < min_dim:
                    print("skipping small rect")
                    continue

                log.write("%s [%d, %d, %d, %d]\n" % (im_file, c[0], c[1], c[2], c[3]) )

                crop_im = im.crop( ( c[0], c[1], c[2], c[3] ) )
                crop_im = crop(crop_im, resolution, crop_mode)

                save(crop_im, out_name, batch_name if sub_dirs else None)
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
        dataset_root = r"/home/twak/archinet/data" #/datawaha/cggroup/kellyt/archinet_backup/complete_2401/data"

    output_folder = f"./dataset_cook_{time.time()}/"

    os.makedirs(output_folder, exist_ok=True)

    if True: # render crops + labels

        json_src = []
        # json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
        json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))
        json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels_2", "*", "*.json")))

        np_data = None  # []

        for f in json_src:
            # render_labels_per_crop(dataset_root, f, output_folder, folder_per_batch=True, res=640, mode='square_crop', np_data=np_data)
            render_labels_per_crop(dataset_root, f, output_folder, folder_per_batch=False, res=512, mode='square_crop', np_data=np_data)

        if np_data is not None:
            all_data = np.concatenate(tuple(np_data), 0)
            print(f"mean [{np.mean(all_data, axis=(0,1))}] std [{np.std(all_data, axis=(0,1))}]")
    else: # render only crops
    # generate dataset from all metadata_single_element
        photo_src = []
        photo_src.extend(glob.glob(r'./photos/*/*.JPG'))
        photo_src.extend(glob.glob(r'./photos/*/*.jpg'))
        render_crops(photo_src, output_folder, crop_mode="square_crop", resolution=512, quality=95, sub_dirs=True)