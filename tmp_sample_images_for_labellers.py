import glob
import hashlib
import json
import os
import random
import time
from pathlib import Path
import PIL
from PIL import Image, ImageOps


# script 18th July 2022 to second set of 1500 crops from dataset to send the labellers

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


from itertools import filterfalse

seen = build_src_lookup("./metadata_window_labels/from_labellers/input_locations_first_1500.txt")

def in_seen(file):
    global seen
    for s in seen.values():
        batch_name = s['src'].split("\\")
        if batch_name[0].strip() in file and batch_name[1].strip() in file:
            print(f"rejecting image from last set {file}")
            return False
    return True

batches = os.listdir("./photos")

photos = []
photos.extend(glob.glob(r'./photos/*/*.jpg'))
photos.extend(glob.glob(r'./photos/*/*.JPG'))
# photos.extend(glob.glob(r'./photos/*/*9511.JPG'))

photos[:] = filter(in_seen, photos)


# json_src.extend(glob.glob( os.path.join (dataset_root, "metadata_window_labels", "*", "*.json" ) ) )


output_dir = f"./metadata_single_elements/to_labellers_cook{time.time()}"
os.makedirs(output_dir,exist_ok=True)

log = open(os.path.join(output_dir, 'log.txt'), "w")

COUNT = 0

while COUNT < 2500:

    photo = random.choice(photos)

    print(f"{COUNT} : {photo}")

    batch = Path(photo).parent.name
    if ("vienna" in batch or "Vienna" in batch) and random.random() < 0.3: # downsample boring grey vienna
        print ("skipping Wein")
        continue

    min_dim = 1024

    out_name, out_ext = os.path.splitext(os.path.basename(photo))
    json_file = Path(photo).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch).joinpath(f"{out_name}.json")

    if os.path.exists(os.path.join (".",json_file ) ): # crop

        im = ImageOps.exif_transpose(Image.open(photo))

        prev = json.load(open(json_file, "r") )
        rects = prev["rects"]

        tags = []

        if "tags" in prev:
            tags = prev["tags"]

        if 'deleted' in tags:
            print("skipping deleted")
            continue

        r = random.choice(rects)

        if "window" not in r[1] and "glass_facade" not in r[1] and "shop" not in r[1] and "church" not in r[1] and "abnormal" not in r[1]:
            print("skipping not-a-window " + " ".join(tags))
            continue

        r = r[0]

        if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
            print("skipping small rect")
            continue

        log.write("%s\a%s%s [%d, %d, %d, %d]\n" % (batch, out_name, out_ext, r[0], r[1], r[2], r[3]) )

        im = im.crop( ( r[0], r[1], r[2], r[3] ) )

        md5hash = hashlib.md5(im.tobytes())

        jpg_out_file = "%s.jpg" % md5hash.hexdigest()

        log.write("\"%s\"\n" % jpg_out_file)

        out_path = os.path.join(output_dir, jpg_out_file)

        if (os.path.exists(out_path)):
            print("skipping; duplicate hash!")
            continue


        im.save(out_path, format="JPEG", quality=90)
        COUNT += 1
        log.flush()
    else:
        print("skipping missing json file")


log.close()
