import glob
import os
import sys
from pathlib import Path
from random import shuffle


def split(rgb_files, output_split=[[50, "val"], [50, "test"]]):
    shuffle(rgb_files)

    nses = []
    total = 0

    for p, n in output_split:
        total += p
        fh = Path(f"{n}.txt").open(mode="w")
        nses.append([total, p, n, fh])

    # if total > len(rgb_files):
    #     print("error, not enough data!")
    #     return

    cpi = 0
    for i, rgb in enumerate(rgb_files):
        print(f"adding {i} {rgb}")

        tpn = nses[cpi]
        prgb = Path(rgb)
        fh = tpn[3]
        basename = os.path.splitext(prgb.name)[0]

        fh.write(basename + "\n")

        if i > nses[cpi][0]:  # cumulative > i
            cpi += 1

        if cpi >= len(nses):
            print("done")
            break

    for _, _, _, fh in nses:
        fh.close()


rgbs = []
name = sys.argv[1]

rgbs.extend(glob.glob(os.path.join(rf"/ibex/ai/home/kellyt/winlab_4_png/{name}", "*.png")))

split(rgbs, output_split=[[200, f"{name}_val"], [100000, f"{name}_test"]])

