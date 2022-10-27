import glob
import os
from pathlib import Path
import contextlib

# if blender rendering is interupted, we may not have all data for each image. Delete those which aren't complete...

def valid_syn_pairs(rgb_file):

    path = Path(rgb_file) # png
    lab_file = path.parent.parent.joinpath("labels").joinpath(path.name)
    #lab8_file = path.parent.parent.joinpath("labels_8bit").joinpath(path.name)
    attribs_file = path.parent.parent.joinpath("attribs").joinpath( os.path.splitext(path.name)[0]+".txt")

    print (path)
    good = lambda f: os.path.exists(f) and os.path.getsize(f) > 0
    if good(rgb_file) and good (lab_file) and good(attribs_file): # and good (lab8_file):
        return False
    else:
        with contextlib.suppress(FileNotFoundError):
            print ("removing " + rgb_file)
            # os.remove(rgb_file)
            # os.remove(lab_file)
            # os.remove(lab8_file)
            # os.remove(attribs_file)

        return True

rgbs = []

rgbs.extend(glob.glob(os.path.join( r"/ibex/scratch/kellyt/windowz/winsyn_king/", "rgb", "*.png")))

count =	0
for lab in rgbs:
    if valid_syn_pairs ( lab ):
	    count+=1

print (f"have deleted {count}")
