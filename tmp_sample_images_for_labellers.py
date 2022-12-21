from glob import glob
import hashlib
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path
import PIL
from PIL import Image, ImageOps

import platform

# script 19th December 22 to select unlabelled window crops for labelling.


from itertools import filterfalse

output_dir = f"./metadata_for_labellers/to_labellers_cook{time.time()}"
os.makedirs(output_dir, exist_ok=True)

log = open(os.path.join(output_dir, 'log.txt'), "w")

all_batches = os.listdir("./photos")
# batches = [x for x in batches if "michaela" in x]
# batches.extend(["tom_london_20220418", "tom_york_20220411", "angela_prilep_20221022"])

SEEN = set(glob(os.path.join("./metadata_window_labels", "*", "*.json")))

def not_seen(jpgs):
    global SEEN
    sss = defaultdict(lambda: set())
    out = []

    for s in SEEN:
        sss[Path(s).parent.name].add(Path(s).with_suffix("").name)

    for j in jpgs:
        batch = Path(j).parent.name
        base = Path(s).with_suffix("").name

        if base not in sss[batch]:
            out.append(j)
        # else:
        #     print(f"ignoring already labelled {j}")

    return out

print(all_batches)

for limit, batches, country in [
    (1500, [x for x in all_batches if "michaela_vienna" in x], "austria"),
    (500 , [x for x in all_batches if "michaela_berlin" in x], "germany"),
    (300 , [x for x in all_batches if "tom"             in x], "uk")
    ]:

    print( f"trying to take {limit} photos from {country}" )

    photos = set()
    for b in batches:
        photos.update (glob(f'./photos/{b}/*.jpg'))
        if platform == "linux":
            photos.add(glob(f'./photos/{b}/*.JPG'))

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
