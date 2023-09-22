import random
import shutil
import os
from PIL import Image

outdir = "/ibex/user/kellyt/mix"

'''
create a new dataset that mixes synthetic and real. Create a bunch of split files for different ratios. Trained on 0079_mix
'''

os.makedirs(f"{outdir}/rgb", exist_ok=True)
os.makedirs(f"{outdir}/labels", exist_ok=True)

rlines, slines = [], []

with open("/ibex/user/kellyt/winlab_5/2048.txt", "r") as f:
    rlines = f.readlines()
    # for line in rlines:
    #     print(line)
    #     line = line.strip()
    #     shutil.copyfile("/ibex/user/kellyt/winlab_5/rgb/" + line + ".jpg", f"{outdir}/rgb/{line}.jpg")
    #     shutil.copyfile("/ibex/user/kellyt/winlab_5/labels/" + line + ".png", f"{outdir}/labels/{line}.png")


with open("/ibex/user/kellyt/windowz/winsyn_riyal/16384.txt", "r") as f:
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
        shutil.copyfile("/ibex/user/kellyt/windowz/winsyn_riyal/labels_8bit/" + line + ".png", f"{outdir}/labels/{line}.png")

# fixed real, some synthetic
# for i in range(12, 15):
#
#     for z in range (5) if i <= 16 else [1]:
#         syn = 2 ** i
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
# for i in range(0, 12):
#     for z in range (5):
#         real = 2 ** i
#
#         print(f">>>> {real} {i}")
#
#         with open(f"{outdir}/mix_z{real}_{z}.txt", "w") as f:
#
#             random.shuffle(rlines)
#             random.shuffle(slines)
#
#             lines = [*slines]
#             lines.extend(rlines[:real])
#
#             for line in lines:
#                 line = line.strip()
#                 f.write(f"{line}\n")

