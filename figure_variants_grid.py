import random

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
import svgwrite
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

    try:
        coords = []
        params = open_params(parameters)
        for corner in ["bl", "br", "tr", "tl"]:
            coords.append(((params[win + f"/_{corner}_screen_x"] + 1) * 0.5 * bg.width, (-params[win + f"/_{corner}_screen_y"] + 1) * 0.5 * bg.height))

        bgi.polygon(coords, outline="white", width=5, )
    except:
        print ("skipping rendering a window outline")

    return bg

def create_image_grid(root_directory, split_file):

    svg_out_dir = os.path.join(root_directory, f"svg_out_{time.time()}")
    b = "winsyn_riyal"

    styles = [
        (b, "rgb", "png"),
        (b, "labels", "png"),
        (b, "attribs", "txt"),
        (b, "64ms", "png"),
        (b, "128ms", "png"),
        (b, "256ms", "png"),
        (b, "512ms", "png"),
        (b, "1024ms", "png"),
        (b, "2048ms", "png"),
        (b, "rgb_exposed", "png"),
        (b, "rgb_histomatched", "png"),
        (b, "rgb_exposed_histomatched", "png"),
        (b, "rgb_albedo", "png"),
        (b, "diffuse", "png"),
        (b, "phong_diffuse", "png"),
        (b, "normals", "png"),
        (b, "edges", "png"),
        (b, "col_per_obj", "png"),
        (b, "texture_rot", "png"),
        (b, "voronoi_chaos", "png"),
        (b, "rgb_depth", "exr"),
        (b, "canonical", "png"),
        (b, "canonical_albedo", "png"),
        (b, "canonical_transcol" "png")
    ]

    with open(split_file, 'r') as f:
        splits = f.read().split("\n")

    random.shuffle(splits)
    splits = splits[:num]

    base_image_height = base_image_width = 128

    total_height = len(styles) * base_image_height
    total_width  = num * base_image_width

    grid_image = Image.new('RGB', (total_width, total_height))
    draw = ImageDraw.Draw(grid_image)


    svg_out = svgwrite.Drawing(os.path.join(svg_out_dir, "labels2.svg"), profile='tiny')

    x_offset = 0

    for dataset, name, ext in styles:

        svg_out.add(svg_out.text(f"{dataset}", insert=(x_offset, -1), fill='black', font_size="10px", font_family="monospace"))

        for split in splits:

            image_file = os.path.join ( dataset, name, f"{split}.{ext}" )

            if ext.lower() in ['.jpg', '.png', '.jpeg']:
                base_image = Image.open(image_file)
            elif ext.lower() in ['.exr']:
                base_image = render_depth_image(image_file)
            elif ext.lower() in ['.txt']:
                base_image = render_attribs(image_file)

            base_image = base_image.resize((base_image_width, base_image_height))
            im_filename = f"{dataset}_{name}_{split}_{ext}.jpg"
            base_image.save(os.path.join(svg_out_dir, im_filename), format="JPEG")

            svg_out.add(svg_out.image(href=im_filename, insert=(x_offset, y_offset), size=(width, height)))
            grid_image.paste(base_image, (x_offset, y_offset))

            x_offset += base_image_width
        y_offset += base_image_width


    output_path = os.path.join(root_directory, "image_grid.jpg")
    grid_image.save(output_path)


# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
create_image_grid(directory_path)