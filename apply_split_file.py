import os
import shutil
import sys

with open(sys.args[1]) as f:
    for line in f:
        shutil.copyfile(os.path.join("labels", f"{line}.png"), os.path.join(sys.args[2], "labels", f"{line}.png"))
        shutil.copyfile(os.path.join("rgb", f"{line}.png"), os.path.join(sys.args[2], "rgb", f"{line}.png"))
