import os
import shutil
import sys

dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"], ["attribs", "txt"] ]

with open(sys.argv[1]) as f:
    for line in f:
        print (line)
        line = line.replace("\n", "")

        for dir, ext in dirs:
            os.makedirs(os.path.join(sys.argv[2], dir), exist_ok=True )
            shutil.copyfile(os.path.join(dir, f"{line}.{ext}"), os.path.join(sys.argv[2], dir, f"{line}.{ext}"))
