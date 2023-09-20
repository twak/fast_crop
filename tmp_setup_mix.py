import random
import shutil
import os
from PIL import Image

outdir = "/ibex/user/kellyt/mix"

os.makedirs(f"{outdir}/rgb", exist_ok=True)

rlines, slines = [], []

with open("/ibex/user/kellyt/winlab_5/2048.txt", "r") as f:
    rlines = f.readlines()
    for line in rlines:
        print(line)
        line = line.strip()
        shutil.copyfile("/ibex/user/kellyt/winlab_5/rgb/" + line +".jpg", f"{outdir}/rgb/{line}.jpg")


with open("/ibex/user/kellyt/windowz/winsyn_riyal/2048.txt", "r") as f:
    slines = f.readlines()
    for line in slines:
        print(line)
        line = line.strip()
        img = Image.open(f"/ibex/user/kellyt/windowz/winsyn_riyal/rgb/{line}.png")
        img.save(f"{outdir}/rgb/{line}.jpg", "JPEG", quality=90)


for i in range(5):

    real = 2 ** i
    with open(f"/ibex/user/kellyt/mix/mix_{real}.txt", "w") as f:

        random.shuffle(rlines)
        random.shuffle(slines)

        lines = [*slines]
        lines.extend(rlines[:real])

        for line in lines:
            line = line.strip()
            f.write(f"{line}\n")