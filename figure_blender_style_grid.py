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
    normalized_depth = normalized_depth / normalized_depth.max()

    depth_colormap = plt.cm.magma(normalized_depth)  # Using magma colormap
    depth_colormap = (depth_colormap[:, :, :3] * 255).astype(np.uint8)

    return Image.fromarray(depth_colormap)

def open_params(f):
    with open(f, 'r') as fp:
        txt = fp.read().split("\n")
        txt[-3] = txt[-3].replace(",", "")  # extra comma on final attribute

        return json.loads("".join(txt))

def render_attribs(parameters):

    # create a blank image
    bg = Image.new('RGB', (512, 512))
    bgi = ImageDraw.Draw(bg)

    win = "win_primary"
    coords = []
    params = open_params(parameters)
    for corner in ["bl", "br", "tr", "tl"]:
        coords.append(((params[win + f"/_{corner}_screen_x"] + 1) * 0.5 * bg.width, (-params[win + f"/_{corner}_screen_y"] + 1) * 0.5 * bg.height))

    bgi.polygon(coords, outline="white", width=5, )

    return bg

def create_image_grid(root_directory):

    images = defaultdict(dict)

    styles = [
        "rgb",
        "labels",
        "attribs",
        "64ms",
        "128ms",
        "256ms",
        "512ms",
        "1024ms",
        "2048ms",
        "rgb_exposed",
        "rgb_histomatched",
        "rgb_exposed_histomatched",
        "rgb_albedo",
        "diffuse",
        "phong_diffuse",
        "normals",
        "edges",
        "col_per_obj",
        "texture_rot",
        "voronoi_chaos",
        "rgb_depth",
        "canonical",
        "canonical_albedo",
        "canonical_transcol"
    ]

    for style in styles:
        dir = os.path.join(root_directory, style)
        if os.path.exists(dir):
            for file in os.listdir(dir):
                base_name, extension = os.path.splitext(file)
                if extension.lower() in ['.jpg', '.png', '.jpeg', '.exr', '.txt']:
                    images[style][base_name] = os.path.join(root_directory, style, file)

    base_image_width = 512  # Adjust this to your desired width
    base_image_height = 512  # Adjust this to your desired height

    total_width = len(styles) * base_image_width
    total_height = len(images["rgb"]) * base_image_height

    grid_image = Image.new('RGB', (total_width, total_height))
    draw = ImageDraw.Draw(grid_image)

    x_offset = 0

    for style in styles:

        y_offset = 0

        for file in os.listdir(os.path.join(root_directory, "rgb")):
            base_name, _ = os.path.splitext(file)

            if style in images and base_name in images[style]:
                image_file = images[style][base_name]
                _, extension = os.path.splitext(image_file)

                if extension.lower() in ['.jpg', '.png', '.jpeg']:
                    base_image = Image.open(image_file)
                elif extension.lower() in ['.exr']:
                    base_image = render_depth_image(image_file)
                elif extension.lower() in ['.txt']:
                    base_image = render_attribs(image_file)

                base_image = base_image.resize((base_image_width, base_image_height))
                grid_image.paste(base_image, (x_offset, y_offset))

            y_offset += base_image_width
        x_offset += base_image_width

    draw = ImageDraw.Draw(grid_image)
    font = font_manager.FontProperties(family='sans-serif', weight='bold')
    font = ImageFont.truetype(font_manager.findfont(font), 48)

    for i, style in enumerate ( styles ):
        draw.text((i * base_image_width+ 20, 20), style, font=font)

    output_path = os.path.join(root_directory, "image_grid.jpg")
    grid_image.save(output_path)


# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
create_image_grid(directory_path)