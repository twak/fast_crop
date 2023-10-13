import glob
import os
import random
import sys

import numpy as np
from PIL import Image

from pathlib import Path

from pathlib import Path
import contextlib
import concurrent.futures

def write_mean(dir, count=2048):

    print(f"  == {dir} == ")

    out_file = os.path.join(Path(dir).parent, "means", dir + ".npz")
    if os.path.exists(out_file):
        print(f"skipping {dir}, already exists")
        return

    imgs = []
    imgs.extend(glob.glob(os.path.join(dir, "*.png")))
    imgs.extend(glob.glob(os.path.join(dir, "*.jpg")))

    # if len(sys.argv) > 3:
    #     print (f"using split file {sys.argv[3]}")
    #     with open(os.path.join(".", sys.argv[3]), "r") as f:
    #         for line in f:
    #             imgs.append(os.path.join(".", sys.argv[1], f"{line[:-1]}.jpg"))

    print(f"{len(imgs)} images found")
    random.shuffle(imgs)

    if count > 0:
        print(f"using {count} images for computation")

    if count < len(imgs):
        imgs = imgs[:int(count)]


    if len(imgs) > 0:

        np_data = []

        for f in imgs:
            print (f)
            np_data.append(np.asarray(Image.open(f, "r")))

        all_data = np.concatenate(tuple(np_data), 0)
        mean = np.mean(all_data, axis=(0, 1))
        std  = np.std (all_data, axis=(0, 1))
        print(f"mean=[{mean[0]}, {mean[1]}, {mean[2]}], std=[{std[0]}, {std[1]}, {std[2]}],")

        # save mean and std as npz
        np.savez(out_file, mean=mean, std=std)

        # with open(os.path.join(Path(dir).parent, "means", dir + ".txt"), "w") as f:
        #     f.write(f"mean=[{mean[0]}, {mean[1]}, {mean[2]}], std=[{std[0]}, {std[1]}, {std[2]}],")

    else:
        print("no images found :(")



if __name__ == "__main__":

    _pool = concurrent.futures.ThreadPoolExecutor()

    os.makedirs("means", exist_ok=True)
    # for i in range ( 1, 10 ):
    for dir in ["0cen", "3cen", "6cen", "12cen", "24cen", "48cen", "96cen"]:
    # for dir in ["mono_profile", "no_rectangles","nosplitz","only_rectangles","only_squares","single_window", "wide_windows" ]:
    # for dir in [
    #     "lvl1"
    # ]:
        _pool.submit(write_mean, dir)

print ("all submitted!")

# _d:
# "0cen" ,
#         "128spp" ,
#         "12cen" ,
#         "16spp" ,
#         "1spp" ,
#         "256spp" ,
#         "2cen" ,
#         "2spp" ,
#         "32spp" ,
#         "4cen" ,
#         "4spp" ,
#         "512spp" ,
#         "64spp" ,
#         "8cen" ,
#         "8spp" ,
#         "dayonly" ,
#         "dayonly_exposed" ,
#         "fixedsun" ,
#         "fixedsun_exposed" ,
#         "monomat" ,
#         "nightonly" ,
#         "nightonly_exposed" ,
#         "nobounce" ,
#         "nobounce_exposed" ,
#         "nosun" ,
#         "nosun_exposed" ,
#         "notransmission" ,
#
#
#         "rgb" ,
#         "rgb_albedo" ,
#         "rgb_depth" ,
#         "rgb_exposed"

    # _c
    # for dir, _ in  [["1024ms","png"], ["256ms","png"], ["attribs","txt"], ["edges","png"], ["normals","png"],
    #    ["rgb_albedo","png"], ["texture_rot","png"], ["128ms","png"], ["512ms","png"], ["col_per_obj","png"],
    #    ["labels","png"], ["phong_diffuse","png"], ["voronoi_chaos","png"], ["2048ms","png"], ["64ms","png"],
    #    ["diffuse","png"], ["rgb","png"], ["rgb_histomatched","png"],
    #    ["rgb_exposed","png"], ["rgb_exposed_histomatched","png"] ]:
    #     write_mean(dir)