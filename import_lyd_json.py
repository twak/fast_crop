import glob
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path
import re

def build_src_lookup(lookup_files):
    src_lookup = {}

    for lookup_file in lookup_files:

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


ALL_NAMES = {}
CROPS = {}
JSON_NAMES={}
LAST_PARENT = ""
COUNT2 = 0

def write_label_jsons( src_lookup, lyd_json):

    global ALL_NAMES, LAST_PARENT, CROPS, JSON_NAMES

    # we might have multiple labels from a single image
    # our data-structure assumes information-per-original-photo!
    # the src_lookup contains the correspondence between the photo name and the one back from the labellers

    p = Path(lyd_json)
    parent = p.parent
    if parent != LAST_PARENT:
        # print (f"from {parent.name}        {p.name}:")
        LAST_PARENT = parent

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
            # else:
            #     continue

            src_info = src_lookup[crop_file_name]
            src_file = src_info['src']
            src_region = src_info['crop_region']

            # if src_file in CROPS:
            #     crop_list = CROPS[src_file]
            # else:
            #     crop_list = CROPS[src_file] = []
            #
            # if (src_region in crop_list):
            #     print ("   FAILURE++ ")
            #
            # crop_list.append(src_region)
            #
            # if (len (CROPS[src_file])) > 1:
            #     print (f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {CROPS[src_file]} <<")
            #
            # continue

            src_split = re.split(r'[\\]|[.]', src_file)

            out_file_name = os.path.join(".", "metadata_window_labels", src_split[0], src_split[1]+".json" )
            os.makedirs(Path(out_file_name).parent, exist_ok=True)

            if os.path.exists(out_file_name):
                with open(out_file_name, "r") as f2:
                    annotations_out = json.load(f2)
            else:
                annotations_out = {}

            this_window = dict(labels={})
            annotations_out[crop_file_name] = this_window
            this_window["crop"] = src_region

            if img_id in idx_to_ann:
                global COUNT3
                COUNT3 +=1
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

                with open(out_file_name, "w") as f:
                    json.dump(annotations_out, f)
                    JSON_NAMES[out_file_name] = len ( annotations_out )

                global COUNT
                COUNT += 1

                if crop_file_name not in ALL_NAMES:
                    ALL_NAMES[crop_file_name] = f"{parent.name}\{p.name}"
                    print(f"{len(ALL_NAMES)}  {crop_file_name}")
                else:
                    print(f" this guy mentioned twice: {crop_file_name} in {parent.name}\{p.name}    x (previously in {ALL_NAMES[crop_file_name]})")

            else:

                # if not os.path.exists(os.path.join(root, crop_file_name)):

                # print(f"failed to find matching img_id {crop_file_name} {src_file} {src_region} {lyd_json}")
                pp = Path (lyd_json)
                print(f"failed to find labels img_id {crop_file_name} in {parent.name}\{p.name}")
                global COUNT2
                COUNT2 += 1


json_src = []

# newer corrections from labellers overwrite old version

# for s in ["LYD__KAUST_Batch_1(100images)_16.06.22_", "LYD__KAUST_1_batch_(100_frames)_21.06.2022",
#           "LYD__KAUST_batch_1_fixed_24.06.2022", "LYD__KAUST_batch_2_24.06.2022", "LYD__KAUST_batch2_updated", "LYD__KAUST_batch1_fixed_2tasks", "LYD__KAUST_batch_1_updated", "LYD__KAUST_batch_3_fixed", "LYD__KAUST_batch_4", "LYD__KAUST_batch4_fixed_22.07.22", "LYD__KAUST_batch5_22.07.22", "LYD__KAUST_batch4-5_fixed", "LYD__KAUST_batch_6_04.08.2022", "LYD__KAUST_batch_6_fixed", "LYD__KAUST_batch_7",
#           "LYD__KAUST_batch_6_fixed_24_08", "LYD__KAUST_batch_7_fixed_24_08", "LYD__KAUST_batch_8"]:
#     json_src.extend(glob.glob(rf'C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\{s}\**.json'))

json_src.extend(glob.glob(r'.\old_metadata_window_labels\from_labellers\LYD__KAUST_all_batches\*\**.json'))
json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\LYD__KAUST_batch_9\**.json'))

# src_lookup = build_src_lookup(r"/home/twak/Downloads/input_locations_first_1500.txt")

src_lookup = build_src_lookup([r".\old_metadata_window_labels\from_labellers\input_locations_first_1500.txt",
                               r".\old_metadata_window_labels\from_labellers\input_locations_second_1500.txt"] )


# filter second labellers file

# tmp_out = r"./subset_labellers_second_1500/"
#
# for key, value in src_lookup.items():
#     src = value["src"]
#     srcs = src.split("\\")
#
#     in_p = os.path.join(".", "photos", srcs[0], srcs[1])
#     out_p = os.path.join(".", "subset_labellers_second_1500", srcs[0])
#     os.makedirs(out_p, exist_ok=True)
#     out_p = os.path.join(out_p, srcs[1])
#     shutil.copyfile(in_p, out_p)

COUNT  = 0
COUNT2 = 0
COUNT3 = 0

for f in json_src:
    write_label_jsons( src_lookup, f )

print ( f"processed {COUNT3} index entries in lyd json" )
print (f"unique files mentioned {len ( ALL_NAMES ) }")

total_rects = 0
for i in JSON_NAMES.values():
    total_rects += i

print ( f"{COUNT2} failures" )
print ( f"processed {COUNT} windows" )

print (f"unique json files {len ( JSON_NAMES ) } containing {total_rects} crops")
