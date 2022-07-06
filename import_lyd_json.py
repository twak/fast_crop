import glob
import json
import os
from collections import defaultdict
from pathlib import Path
import re

def build_src_lookup(lookup_file):
    src_lookup = {}

    with open(lookup_file, "r") as index_f:
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


def write_label_jsons( src_lookup, lyd_json, dataset_root = None):

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

            # if crop_file_name != "ee375aa4b1099b7a0649d1fe372138b5.jpg":
            #     continue

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

            if img_id in idx_to_ann:
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

                print ("***********\n")
                print (out_file_name)
                # print (annotations_out)

                with open(out_file_name, "w") as f:
                    json.dump(annotations_out, f)

                global COUNT
                COUNT += 1

#dataset_root = r'C:\Users\twak\Downloads\windowz_1500_1'
#dataset_root = "/home/twak/Downloads/windowz_1500_1/" #
dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"

json_src = []
#json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_batch_1_fixed_24.06.2022\**.json'))
json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_batch_2_24.06.2022\**.json'))
#src_lookup = build_src_lookup(r"/home/twak/Downloads/input_locations_first_1500.txt")
src_lookup = build_src_lookup(r"C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\input_locations_first_1500.txt")

COUNT = 0

for f in json_src:
    write_label_jsons( src_lookup, f, dataset_root=dataset_root)

print ( f"processed {COUNT} windows" )