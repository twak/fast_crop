import os
from PIL import Image

diff = "/home/twak/Downloads/most_improved/winlab"

by_name = []
for f in os.listdir(diff):

    res = f[:-4].split("-")

    by_name.append((float(res[0]), res[-1]))

by_name = sorted (by_name, key=lambda x: -x[0])

with open("/home/twak/Downloads/winlab_5/top_490_best_winlab.txt", "w") as f:
    for score, name in by_name:
        f.write(name+"\n")
        print(f" {name} {score} ")
