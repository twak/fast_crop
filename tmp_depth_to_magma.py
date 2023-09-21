
from PIL import Image, ImageDraw
import os
import fnmatch
import numpy as np
import imageio
import cv2
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import matplotlib.pyplot as plt
from collections import defaultdict

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

import json

def render_depth_image(exr_path):

    normalized_depth = cv2.imread(exr_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)

    normalized_depth = normalized_depth[:, :, 0]

    s = np.percentile(normalized_depth, 5)
    b = np.percentile(normalized_depth, 95)

    normalized_depth = (normalized_depth - s) / (b-s)


    depth_colormap = plt.cm.magma(normalized_depth)  # Using magma colormap
    depth_colormap = (depth_colormap[:, :, :3] * 255).astype(np.uint8)

    return Image.fromarray(depth_colormap)

if __name__ == "__main__":

    path = "/home/twak/Downloads/winsyn_riyal_c"
    for f in os.listdir(path):
        if not f.endswith(".exr"):
            continue

        print (f)
        im = render_depth_image(os.path.join(path, f))
        im.save(os.path.join(path, f + ".png"), "PNG")