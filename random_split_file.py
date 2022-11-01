import glob
import os
import random
import sys
from pathlib import Path

def random_split(location, count):

    label_src = []
    label_src.extend(glob.glob(os.path.join(location, "labels_8bit", "*.png")))
    if len (label_src) < count:
        print("not enough labels!")

    random.shuffle(label_src)

    with open("./split_%d.txt"%count, "w") as split:
        for label in label_src[:count]:
            print (label)
            split.write( os.path.splitext ( Path(label).name)[0] + "\n" )

if __name__ == "__main__":
    random_split ( sys.argv[1], int ( sys.argv[2] ) )