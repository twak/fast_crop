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

    styles = [
        (b, "rgb", "png"),
        (b, "labels", "png"),
        (b, "attribs", "txt"),
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

        (d, "1spp", "png"),
        (d, "2spp", "png"),
        (d, "4spp", "png"),
        (d, "8spp", "png"),
        (d, "16spp", "png"),
        (d, "32spp", "png"),
        (d, "64spp", "png"),
        (d, "128spp", "png"),
        (d, "256spp", "png"),
        (d, "512spp", "png"),

        (d, "monomat", "png"),
        (d, "nightonly", "png"),
        (d, "nightonly_exposed", "png"),
        (d, "nosun", "png"),
        (d, "nosun_exposed", "png"),
        (d, "nobounce", "png"),
        (d, "nobounce_exposed", "png"),
        (d, "fixedsun", "png"),
        (d, "fixedsun_exposed", "png"),
        (d, "dayonly", "png"),
        (d, "dayonly_exposed", "png"),

        (d4, "0cen", "png"),
        (d4, "3cen", "png"),
        (d4, "12cen", "png"),
        (d4, "24cen", "png"),
        (d4, "48cen", "png"),
        (d4, "96cen", "png"),

        (e, "lvl1", "png"),
        (e, "lvl2", "png"),
        (e, "lvl3", "png"),
        (e, "lvl4", "png"),
        (e, "lvl5", "png"),
        (e, "lvl6", "png"),
        (e, "lvl7", "png"),
        (e, "lvl8", "png"),
        (e, "lvl9", "png"),

        (f, "no_rectangles", "png"),
        (f, "only_squares", "png"),
        (f, "nosplitz", "png"),
        (f, "only_rectangles", "png"),
        (f, "single_window", "png"),
        (f, "wide_windows", "png"),
        (f, "mono_profile", "png"),
        
        

    # (b, "canonical", "png"),
        # (b, "canonical_albedo", "png"),
        # (b, "canonical_transcol" "png")
    ]

    # with open(split_file, 'r') as f:
    #     splits = f.read().split("\n")

    # random.shuffle(splits)
    # splits = splits[:num]

    num = 2
    base_image_height = base_image_width = 128

    total_height = len(styles) * base_image_height
    total_width  = num * base_image_width

    grid_image = Image.new('RGB', (total_width, total_height))

    svg_out_dir = os.path.join(root_directory, f"svg_out_{time.time()}")
    os.makedirs(svg_out_dir, exist_ok=True)
    # draw = ImageDraw.Draw(grid_image)
    svg_out = svgwrite.Drawing(os.path.join(svg_out_dir, "labels2.svg"), profile='tiny')


    x_offset = 0
    y_offset = 0

    for dataset, name, _ in styles:


        svg_out.add(svg_out.text(f"{dataset}", insert=(x_offset, -1), fill='black', font_size="10px", font_family="monospace"))

        image_files = os.listdir(os.path.join(root_directory, dataset, name))
        random.shuffle(image_files)

        for image_file in image_files[:num]:
            print (f"{name}: {image_file}")
        # for split in splits:

            # image_file = os.path.join ( dataset, name, f"{split}.{ext}" )
            ext = os.path.splitext(image_file)[1]

            image_filef = os.path.join(os.path.join(root_directory, dataset, name, image_file) )

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
            svg_out.add(svg_out.text(name+"\n23.0", insert=(x_offset, y_offset + base_image_height / 2) ))
            grid_image.paste(base_image, (x_offset, y_offset))

            x_offset += base_image_width
        y_offset += base_image_width

    svg_out.save()
    output_path = os.path.join(root_directory, "image_grid.jpg")
    grid_image.save(output_path)


# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
create_image_grid(directory_path)