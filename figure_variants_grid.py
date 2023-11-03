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
import time

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
        txt[-3] = txt[-3].replace(",")  # extra comma on final attribute

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

def create_image_grid(root_directory):


    b  = "winsyn_riyal"
    d  = "winsyn_riyal_d"
    d4 = "winsyn_riyal_d4"
    e  = "winsyn_riyal_e"
    f  = "winsyn_riyal_f"

    with open(os.path.join("winsyn_riyal", "2048.txt"), "r") as fp: # read the splits for 'two'
        sa = fp.read().split("\n")[:-1]

    with open(os.path.join("winsyn_riyal_f", "2048.txt"), "r") as fp: # read the splits for 'two'
        sf = fp.read().split("\n")[:-1]

    styles = [
        (b, "rgb", "png", sa),
        (b, "labels", "png", sa),
        # (b, "attribs", "txt"),
        (b, "rgb_exposed", "png", sa),
        (b, "rgb_histomatched", "png", sa),
        (b, "rgb_exposed_histomatched", "png", sa),
        (b, "rgb_albedo", "png", sa),
        (b, "diffuse", "png", sa),
        (b, "phong_diffuse", "png", sa),
        (b, "normals", "png", sa),
        (b, "edges", "png", sa),
        (b, "col_per_obj", "png", sa),
        (b, "texture_rot", "png", sa),
        (b, "voronoi_chaos", "png", sa),
        (b, "rgb_depth", "exr", sa),

        (d, "1spp", "png", sa),
        (d, "2spp", "png", sa),
        (d, "4spp", "png", sa),
        (d, "8spp", "png", sa),
        (d, "16spp", "png", sa),
        (d, "32spp", "png", sa),
        (d, "64spp", "png", sa),
        (d, "128spp", "png", sa),
        (d, "256spp", "png", sa),
        (d, "512spp", "png", sa),

        (d, "monomat", "png", sa),
        (d, "nightonly", "png", sa),
        (d, "nightonly_exposed", "png", sa),
        (d, "nosun", "png", sa),
        (d, "nosun_exposed", "png", sa),
        (d, "nobounce", "png", sa),
        (d, "nobounce_exposed", "png", sa),
        (d, "fixedsun", "png", sa),
        (d, "fixedsun_exposed", "png", sa),
        (d, "dayonly", "png", sa),
        (d, "dayonly_exposed", "png", sa),

        (d4, "0cen", "png", sa),
        (d4, "3cen", "png", sa),
        (d4, "12cen", "png", sa),
        (d4, "24cen", "png", sa),
        (d4, "48cen", "png", sa),
        (d4, "96cen", "png", sa),

        (e, "lvl1", "png", sa),
        (e, "lvl2", "png", sa),
        (e, "lvl3", "png", sa),
        (e, "lvl4", "png", sa),
        (e, "lvl5", "png", sa),
        (e, "lvl6", "png", sa),
        (e, "lvl7", "png", sa),
        (e, "lvl8", "png", sa),
        (e, "lvl9", "png", sa),

        (f, "no_rectangles", "png", sf),
        (f, "only_squares", "png", sf),
        (f, "nosplitz", "png", sf),
        (f, "only_rectangles", "png", sf),
        (f, "single_window", "png", sf),
        (f, "wide_windows", "png", sf),
        (f, "mono_profile", "png", sf),
        
        

    # (b, "canonical", "png"),
        # (b, "canonical_albedo", "png"),
        # (b, "canonical_transcol" "png")
    ]

    # with open(split_file, 'r') as f:
    #     splits = f.read().split("\n")

    # random.shuffle(splits)
    # splits = splits[:num]

    num = 16
    base_image_height = base_image_width = 128

    total_height = len(styles) * base_image_height
    total_width  = num * base_image_width

    grid_image = Image.new('RGB', (total_width, total_height))

    svg_out_dir = os.path.join(root_directory, f"svg_out_{time.time()}")
    os.makedirs(svg_out_dir, exist_ok=True)
    # draw = ImageDraw.Draw(grid_image)
    svg_out = svgwrite.Drawing(os.path.join(svg_out_dir, "labels2.svg"), profile='tiny')


    y_offset = 0

    for dataset, name, ext, splits in styles:

        x_offset = 0
        svg_out.add(svg_out.text(f"{dataset}", insert=(x_offset, -1), fill='black', font_size="10px", font_family="monospace"))
        svg_out.add(svg_out.text(name + "\n23.0", insert=(x_offset - base_image_width, y_offset + base_image_height / 2)))

        for split in splits[:num]:

            image_file = os.path.join ( dataset, name,  )
            print (f"{name}: {split}.{ext}")

            # ext = os.path.splitext(image_file)[1]

            image_filef = os.path.join(os.path.join(root_directory, dataset, name, f"{split}.{ext}" ) )

            if ext.lower() in ['.jpg', '.png', '.jpeg']:
                base_image = Image.open(image_filef)
            elif ext.lower() in ['.exr']:
                base_image = render_depth_image(image_filef)
            elif ext.lower() in ['.txt']:
                base_image = render_attribs(image_filef)

            base_image = base_image.resize((base_image_width, base_image_height)).convert('RGB')
            im_filename = f"{dataset}_{name}_{image_file}.jpg"
            base_image.save(os.path.join(svg_out_dir, im_filename), format="JPEG")

            svg_out.add(svg_out.image(href=im_filename, insert=(x_offset, y_offset), size=(base_image_width, base_image_width)))

            grid_image.paste(base_image, (x_offset, y_offset))

            x_offset += base_image_width
        y_offset += base_image_width

    svg_out.save()
    output_path = os.path.join(root_directory, "image_grid.jpg")
    grid_image.save(output_path)


# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
create_image_grid(directory_path)