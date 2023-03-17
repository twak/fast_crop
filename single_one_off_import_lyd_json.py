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

def write_label_jsons( lyd_json):

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

        if 'images' in vals: # multi-image format
            for idx_info in vals['images']:
                idx_to_img[idx_info['id']] = idx_info
        else: # single image format
            idx_to_img[0] = dict(file_name=p.name)

        cdx_to_category = {}
        for idx, c_info in enumerate( vals['categories']["label"]["labels"]):
            cdx_to_category[idx] = c_info['name']

        crop_file_name =   os.path.splitext ( p.name )[0]  #idx_info["file_name"]

        src_info = src_lookup[crop_file_name+".jpg"]
        src_region = src_info['crop_region']


        out_file_name = os.path.join(parent.parent,  "labels_"+ Path(lyd_json).parent.name, os.path.splitext ( crop_file_name )[0] +".json" )
        os.makedirs( Path ( out_file_name ).parent, exist_ok=True)

        if os.path.exists(out_file_name):
            with open(out_file_name, "r") as f2:
                for_json_out = json.load(f2)
        else:
            for_json_out = {}

        this_crop = dict(labels=[])
        for_json_out[crop_file_name] = this_crop
        this_crop["crop"] = src_region

        vert_count = 0
        poly_count = 0
        cats = []

        this_crop['labels'] = polies_out = [] # layered list of polygons (lowest first)

        prev = None
        for ann in vals['item']['annotations']:

            cat_name = cdx_to_category[ann["label_id"]]

            cats.append(cat_name)
            if "points" in ann:
                polygon = ann["points"]
                poly_count += len (polygon)

                poly_out = []
                vert_count += len ( polygon) /2
                for i in range ( int ( len ( polygon) /2 ) ):
                    poly_out.append( ( polygon[i*2], polygon[i*2+1] ) )

                if len (poly_out) > 0:
                    if prev is not None and prev[0] == cat_name: # group those with the same category
                        prev[1].append(poly_out)
                    else:
                        prev = (cat_name, [poly_out])
                        polies_out.append (prev)

        with open(out_file_name, "w") as f2:
            json.dump(for_json_out, f2)
            JSON_NAMES[out_file_name] = len ( for_json_out )

        global COUNT, TOTAL_VERTS, TOTAL_POLYGONS, CAT_COUNT
        COUNT += 1


if __name__ == "__main__":

    json_src = []

    # newer corrections from labellers overwrite old version

    # for s in ["LYD__KAUST_Batch_1(100images)_16.06.22_", "LYD__KAUST_1_batch_(100_frames)_21.06.2022",
    #           "LYD__KAUST_batch_1_fixed_24.06.2022", "LYD__KAUST_batch_2_24.06.2022", "LYD__KAUST_batch2_updated", "LYD__KAUST_batch1_fixed_2tasks", "LYD__KAUST_batch_1_updated", "LYD__KAUST_batch_3_fixed", "LYD__KAUST_batch_4", "LYD__KAUST_batch4_fixed_22.07.22", "LYD__KAUST_batch5_22.07.22", "LYD__KAUST_batch4-5_fixed", "LYD__KAUST_batch_6_04.08.2022", "LYD__KAUST_batch_6_fixed", "LYD__KAUST_batch_7",
    #           "LYD__KAUST_batch_6_fixed_24_08", "LYD__KAUST_batch_7_fixed_24_08", "LYD__KAUST_batch_8", "LYD__KAUST_all_batches_old", "LYD__KAUST_all_batches", "LYD__KAUST_batch_9" ]:
    #     json_src.extend(glob.glob(rf'C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\{s}\**.json'))

    json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\windows_part3\lyd_15_3_to_val\**.json'))
    # json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\LYD__KAUST_batch_9\**.json'))
    src_lookup = build_src_lookup([r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_3.txt",
                                   r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_4.txt"])
    # src_lookup = build_src_lookup([r".\old_metadata_window_labels\from_labellers\input_locations_first_1500.txt",
    #                                r".\old_metadata_window_labels\from_labellers\input_locations_second_1500.txt"] )


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
    CITY_COUNT = {}
    TOTAL_VERTS = 0
    TOTAL_POLYGONS = 0
    CAT_COUNT = {}

    for f in json_src:
        print(f)
        write_label_jsons( f )

    print ( f"processed {COUNT3} index entries in lyd json" )
    print (f"unique files mentioned {len ( ALL_NAMES ) }")

    total_rects = 0
    for i in JSON_NAMES.values():
        total_rects += i

    print ( f"{COUNT2} failures" )
    print ( f"processed {COUNT} windows" )

    print (f"unique json files {len ( JSON_NAMES ) } containing {total_rects} crops\n")

    for c,n in CITY_COUNT.items():
        print( f"{c}, {n}")

    print("\n")

    for c,n in CAT_COUNT.items():
        print( f"{c}, {n}")

    print (f"total verts {TOTAL_VERTS}, total polys {TOTAL_POLYGONS}")