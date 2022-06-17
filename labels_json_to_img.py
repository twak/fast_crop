import copy
import glob
import json

# from the index file when we created the crops for the labellers to our src coordinate system
import os
import random
from collections import defaultdict
from os import path
from pathlib import Path
import re
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
from PIL import ImageOps

dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"

def render(dataset_root, photo_file, json_file):

    colors = {}
    colors["window pane"] = (135, 170, 222)
    colors["window frame"] = (255, 128, 128)
    colors["open-window"] = (0,0,0)
    colors["wall frame"] = (233, 175, 198)
    colors["wall"] = (204,204,204)
    colors["door"] = (164, 120, 192)
    colors["shutter"] = (255, 153, 85)
    colors["blind"] = (255, 230, 128)
    colors["bars"] = (110, 110, 110)
    colors["balcony"] = (222,170,135)
    colors["misc object"] = (174,233,174)

    # colors_transparent = copy.deepcopy (colors)
    # for key, c in colors_transparent.items():
    #     colors_transparent[key] = [*c, 128]

    # read src input
    photo = Image.open(os.path.join (dataset_root, "photos", photo_file) )
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


    # draw polygons


    #
    # image = Image.new("RGB", (640, 480))
    #
    # draw = ImageDraw.Draw(image)
    #
    # # points = ((1,1), (2,1), (2,2), (1,2), (0.5,1.5))
    # points = ((100, 100), (200, 100), (200, 200), (100, 200), (50, 150))
    # draw.polygon((points), fill=200)
    #
    # image.show()

    # save full-res labels directory as png
    # save full-res transparency as jpg
    # ??for image and each crop delete existing thumbnails + html page???

    # in web-script:
    #   when crop img thumbs, also crop label thumbs at 2x1 showing labels
    #   show full-res labels full-size
    #   links to json + transparency are automatic
    #   each metadata folder as tag to each crop and photo
    #   ...run lazy script again...

def build_src_lookup(dataset_root):
    src_lookup = {}

    with open(r"C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\input_locations_first_1500.txt", "r") as index_f:
        lines = index_f.readlines()
        for i in range(int(len(lines) / 2)):
            img_line = lines[i * 2]
            crop_line = lines[i * 2 + 1].replace('"', '').strip()
            splits = img_line.split("[")
            src_file_name = splits[0]
            crop_region = splits[1].replace("]", "").strip()
            crop_region = [*map(lambda x: int(x.strip()), crop_region.split(","))]
            src_lookup[crop_line] = dict(src=src_file_name, crop_region=crop_region)

    return src_lookup


def write_label_jsons(dataset_root, src_lookup, lyd_json):



    # we might have multiple labels from a single image
    # our data-structure assumes information-per-original-photo!
    # the src_lookup contains the correspondence between the photo name and the one back from the labellers
    with open(lyd_json, "r") as f:
        vals = json.load(f)

        idx_to_img = {}

        for idx_info in vals['images']:
            idx_to_img[idx_info['id']] = idx_info

        cdx_to_category = {}
        for c_info in vals['categories']:
            cdx_to_category[c_info['id']] = c_info['name']

        idx_to_ann = defaultdict( list )

        for ann in vals['annotations']:
            idx_to_ann[ann['image_id']].append(ann)

        for img_id, idx_info in idx_to_img.items():

            crop_file_name = idx_info["file_name"]
            src_info = src_lookup[crop_file_name]
            src_file = src_info['src']
            src_region = src_info['crop_region']

            src_split = re.split(r'[\\]|[.]', src_file)

            out_file_name = os.path.join(dataset_root, "metadata_window_labels", src_split[0], src_split[1]+".json" )
            os.makedirs(Path(out_file_name).parent, exist_ok=True)

            if os.path.exists(out_file_name):
                with open(out_file_name, "r") as f:
                    annotations_out = json.load(f)
            else:
                annotations_out = {}

            this_window = dict(labels={})
            annotations_out[crop_file_name] = this_window
            this_window["crop"] = src_region

            for ann in idx_to_ann.get(img_id):
                cat_name = cdx_to_category[ann["category_id"]]

                polygon = ann["segmentation"]
                polies_out = []

                for poly2 in polygon:
                    poly_out = []
                    for i in range ( int ( len ( poly2) /2 ) ):
                        poly_out.append( ( poly2[i*2], poly2[i*2+1] ) )
                    if len (poly_out) > 0:
                        polies_out.append (poly_out)

                if cat_name in this_window['labels']:
                    polygon_list = this_window['labels'][cat_name]
                else:
                    polygon_list = []
                    this_window['labels'][cat_name] = polygon_list

                polygon_list.extend(polies_out)

            print ("***********  \n\n\n")
            print (out_file_name)
            print (annotations_out)

            with open(out_file_name, "w") as f:
                json.dump(annotations_out, f)

            render (dataset_root, src_file, out_file_name)

json_src = []
json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_Batch_1(100images)_16.06.22_\**.json'))
src_lookup = build_src_lookup(dataset_root)

for f in json_src:
    write_label_jsons(dataset_root, src_lookup, f)