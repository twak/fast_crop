import glob
import os
from pathlib import Path

def valid_syn_pairs(rgb_file):

    path = Path(rgb_file) # png
    lab_file = path.parent.joinpath("labels").joinpath(path.name)
    lab8_file = path.parent.joinpath("labels_8_bit").joinpath(path.name)

    good = lambda f: os.path.exists(f) and os.path.getsize(f) > 0

    if good(rgb_file) and good (lab_file) and good (lab8_file):
        return
    else:
        print ("removing " + rgb_file)
        # os.remove(rgb_file)
        # os.remove(lab_file)
        # os.remove(lab8_file)

rgbs = []

rgbs.extend(glob.glob(os.path.join( r"/ibex/scratch/kellyt/windowz/dataset_queen/", "rgb", "*.png")))

for lab in rgbs:
    valid_syn_pairs ( lab, r"/ibex/scratch/kellyt/windowz/dataset_queen/labels_8bit" )