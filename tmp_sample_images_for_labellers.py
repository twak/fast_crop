from glob import glob
import hashlib
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageOps
from sys import platform

# script 19th December 22 to select unlabelled window crops for labelling.
# updated Feb 6th to update



from itertools import filterfalse

import process_labels

output_dir = f"./metadata_for_labellers/to_labellers_cook{time.time()}"
os.makedirs(output_dir, exist_ok=True)

log = open(os.path.join(output_dir, 'log.txt'), "w")

all_batches = os.listdir(r"./photos")
# batches = [x for x in batches if "michaela" in x]
# batches.extend(["tom_london_20220418", "tom_york_20220411", "angela_prilep_20221022"])


LOG_LOOKUP = defaultdict(lambda: set())

with open(r"../log_part_3.txt", "r") as index_f: # images from previous log file
    lines = index_f.readlines()
    for i in range(int(len(lines) / 2)):
        img_line = lines[i * 2]
        crop_line = lines[i * 2 + 1].replace('"', '').strip()
        splits = img_line.split("[")
        src_file_name = splits[0]
        # crop_region = splits[1].replace("]", "").strip()
        # crop_region = [*map(lambda x: int(x.strip()), crop_region.split(","))]
        LOG_LOOKUP[Path(src_file_name).parent.name].add(Path(src_file_name).with_suffix("").name)

print (f"exluding {sum([item for sublist in LOG_LOOKUP for item in sublist])} looking at log file")

# SEEN =
# SEEN = set(glob(os.path.join("./metadata_window_labels", "*", "*.json")))
# SSS = defaultdict(lambda: set())
for s in set(glob(os.path.join(r"./metadata_window_labels", "*", "*.json"))): # already completely labelled images
    LOG_LOOKUP[Path(s).parent.name].add(Path(s).with_suffix("").name)

print (f"exluding {sum([item for sublist in LOG_LOOKUP for item in sublist])} including existing labels")

def not_seen(jpgs):
    global LOG_LOOKUP
    out = []

    for j in jpgs:
        ba = Path(j).parent.name
        base = Path(j).with_suffix("").name

        if base not in LOG_LOOKUP[ba]:
            out.append(j)

    return out

print(all_batches)


for limit, batches, country in [
    (2500, ["peter_washington_20221129", "kaitlyn_ny_20221205", "brian_la_20220905", "scarlette_chicago_20221022", "kalinia_la_20230128"], "usa"),
    # (500 , [x for x in all_batches if "michaela_berlin" in x], "germany"),
    # (300 , [x for x in all_batches if "tom"             in x], "uk")
    ]:

    print( f"trying to take {limit} photos from {country}" )

    photos = set()
    for b in batches:
        photos.update(glob(f'./photos/{b}/*.jpg'))
        if platform == "linux":
            photos.update(glob(f'./photos/{b}/*.JPG'))

    print( f"  found {len(photos)} photos" )
    photos = not_seen(photos)
    print(f"  and after removing labelled we have {len(photos)} photos" )

    COUNT = 0

    while COUNT < limit and len(photos) > 0:

        photo = random.sample(photos, k= 1)[0]
        photos.remove(photo)

        print(f"{COUNT} : {photo}")

        batch = Path(photo).parent.name

        min_dim = 2048

        out_name, out_ext = os.path.splitext(os.path.basename(photo))
        json_file = Path(photo).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch).joinpath(f"{out_name}.json")

        if os.path.exists(os.path.join (".",json_file ) ): # crop

            prev = json.load(open(json_file, "r") )
            im = process_labels.open_and_rotate( photo, prev )

            rects = prev["rects"]

            tags = []

            if "tags" in prev:
                tags = prev["tags"]

            if 'deleted' in tags:
                print("skipping deleted")
                continue

            r = random.choice(rects)

            if "window" not in r[1] and "glass_facade" not in r[1] and "shop" not in r[1] and "church" and "door" not in r[1] and "abnormal" not in r[1]:
                print("skipping not-a-window " + " ".join(tags))
                continue

            r = r[0]

            if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
                print("skipping small rect")
                continue

            im = im.crop( ( r[0], r[1], r[2], r[3] ) )

            md5hash = hashlib.md5(im.tobytes())

            jpg_out_file = "%s.jpg" % md5hash.hexdigest()

            log.write("%s\\%s%s [%d, %d, %d, %d]\n" % (batch, out_name, out_ext, r[0], r[1], r[2], r[3]))
            log.write("%s\n" % jpg_out_file)

            out_path = os.path.join(output_dir, country, jpg_out_file)
            os.makedirs(Path(out_path).parent, exist_ok=True)

            if os.path.exists(out_path):
                print("skipping; duplicate hash!")
                continue

            im.save(out_path, format="JPEG", quality=80)
            COUNT += 1
            log.flush()
        else:
            print("skipping: missing json file")

log.close()
print(f"wrote dataset to {output_dir}")
