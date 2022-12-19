import os
import shutil
import sys

dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"], ["attribs", "txt"] ]

with open(sys.argv[1]) as f:
    for line in f:

        line = line.replace("\n", "")
        print(line)
        for dur, ext in dirs:
            os.makedirs(os.path.join(sys.argv[2], dur), exist_ok=True)
            shutil.copyfile(os.path.join(dur, f"{line}.{ext}"), os.path.join(sys.argv[2], dur, f"{line}.{ext}"))
