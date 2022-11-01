import glob
import os
import sys
from pathlib import Path
import contextlib
import concurrent.futures

# if blender rendering is interupted, we may not have all data for each image. Delete those which aren't complete...
from PIL import Image

def valid_syn_pairs(rgb_file):

    path = Path(rgb_file) # png
    lab_file = path.parent.parent.joinpath("labels").joinpath(path.name)
    lab8_file = path.parent.parent.joinpath("labels_8bit").joinpath(path.name)
    attribs_file = path.parent.parent.joinpath("attribs").joinpath( os.path.splitext(path.name)[0]+".txt")

    print (path)
    good = lambda f: os.path.exists(f) and os.path.getsize(f) > 0

    bad = False
    try:
        a = Image.open(rgb_file, "r")    # albedo dataset causing issues
        b = Image.open(lab8_file, "r")
        a.verify()
        b.verify()
        if a is None or b is None:
            bad = True
    except:
        bad = True

    if good(rgb_file) and good (lab_file) and good(attribs_file) and good (lab8_file) and not bad:
        return 0 # good
    else:
        with contextlib.suppress(FileNotFoundError):

            if not good(rgb_file): print("missing rgb")
            if not good(lab_file): print("missing lab")
            if not good(attribs_file): print("missing attribs")
            if not good(lab8_file): print("missing lab8")

            if len (sys.argv) > 2:
                print("removing " + rgb_file)
                os.remove(rgb_file)
                os.remove(lab_file)
                os.remove(lab8_file)
                os.remove(attribs_file)
            else:
                print("if this wasn't a dry run, I'd be removing " + rgb_file)

        return 1 # bad

#rgbs = []

#rgbs.extend(glob.glob(os.path.join( r"/ibex/scratch/kellyt/windowz/winsyn_king/", "rgb", "*.png")))


_pool = concurrent.futures.ThreadPoolExecutor()

rgbs = []

rgbs.extend(glob.glob(os.path.join( sys.argv[1], "rgb", "*.png")))

processes = []
count = 0
for rgb in rgbs:

    processes.append(_pool.submit ( valid_syn_pairs, rgb ))

    for r in concurrent.futures.as_completed(processes):
        count += r.result()

# count =	0
# for lab in rgbs:
#     if valid_syn_pairs ( lab ):
# 	    count+=1
if len (sys.argv) > 2:
    print (f"have deleted {count}")
else:
    print(f"if this wasn't a dry run, I would have deleted {count}")
