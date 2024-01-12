import random
import shutil
import os
from PIL import Image

outdir = "/ibex/user/kellyt/mix"

'''
create a new dataset that mixes synthetic and real. Create a bunch of split files for different ratios. Trained on 0079_mix
'''

os.makedirs(f"{outdir}/rgb", exist_ok=True)
os.makedirs(f"{outdir}/labels_easy4", exist_ok=True)

rlines, slines = [], []

with open("/ibex/user/kellyt/winlab_5/easy_train.txt", "r") as f:
# with open("/ibex/user/kellyt/winlab_5/2048.txt", "r") as f:
    rlines = f.readlines()
    for line in rlines:
        print(line)
        line = line.strip()
        shutil.copyfile("/ibex/user/kellyt/winlab_5/rgb/" + line + ".jpg", f"{outdir}/rgb/{line}.jpg")
        shutil.copyfile("/ibex/user/kellyt/winlab_5/labels_easy4/" + line + ".png", f"{outdir}/labels_easy4/{line}.png")


# with open("/ibex/user/kellyt/windowz/winsyn_riyal/16384.txt", "r") as f:
with open("/ibex/user/kellyt/windowz/winsyn_riyal/2048.txt", "r") as f:
    slines = f.readlines()
    for line in slines:
        print(line)
        line = line.strip()

        op = f"{outdir}/rgb/{line}.jpg"

        if os.path.exists(op):
            continue

        img = Image.open(f"/ibex/user/kellyt/windowz/winsyn_riyal/rgb/{line}.png")
        img = img.convert("RGB")

        # background = Image.new('RGBA', img.size, (255, 255, 255))
        # alpha_composite = Image.alpha_composite(background, img)

        img.save(op, "JPEG", quality=90)
        shutil.copyfile("/ibex/user/kellyt/windowz/winsyn_riyal/labels_easy4/" + line + ".png", f"{outdir}/labels_easy4/{line}.png")

# fixed real, some synthetic
# for i in range(12, 15):
#
#     syn = 2 ** i
#
#     for z in range (5) if i <= 16 else [1]:
#
#         print(f">>>> {syn} {i}")
#
#         with open(f"{outdir}/real_{syn}_{z}.txt", "w") as f:
#
#             random.shuffle(rlines)
#             random.shuffle(slines)
#
#             lines = [*rlines]
#             lines.extend(slines[:syn])
#
#             for line in lines:
#                 line = line.strip()
#                 f.write(f"{line}\n")

# fixed synthetic, some real
for i in range(1, 12):

    real = 2 ** i  # 2...2048 inclusive
    print(f">>>> {real} {i}")

    with open(f"{outdir}/easy_mix_{real}.txt", "w") as f:

        # random.shuffle(rlines)
        # random.shuffle(slines)

        lines = [*slines]
        lines.extend(rlines[:real])

        random.shuffle(lines)

        for line in lines:
            line = line.strip()
            f.write(f"{line}\n")

