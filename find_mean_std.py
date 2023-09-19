import glob
import os
import random
import sys

import numpy as np
from PIL import Image

from pathlib import Path

def write_mean(dir, count=2048):

    print(f"  == {dir} == ")

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
        np.savez(os.path.join(Path(dir).parent, "means", dir + ".npz"), mean=mean, std=std)

        # with open(os.path.join(Path(dir).parent, "means", dir + ".txt"), "w") as f:
        #     f.write(f"mean=[{mean[0]}, {mean[1]}, {mean[2]}], std=[{std[0]}, {std[1]}, {std[2]}],")

    else:
        print("no images found :(")



if __name__ == "__main__":

    os.path.makedirs("means", exist_ok=True)

    for dir, _ in  [["1024ms","png"], ["256ms","png"], ["attribs","txt"], ["edges","png"], ["normals","png"],
       ["rgb_albedo","png"], ["texture_rot","png"], ["128ms","png"], ["512ms","png"], ["col_per_obj","png"],
       ["labels","png"], ["phong_diffuse","png"], ["rgb_depth","exr"], ["voronoi_chaos","png"], ["2048ms","png"], ["64ms","png"],
       ["diffuse","png"], ["labels_8bit","png"], ["rgb","png"], ["rgb_histomatched","png"],
       ["rgb_exposed","png"], ["rgb_exposed_histomatched","png"] ]:
        write_mean(dir)