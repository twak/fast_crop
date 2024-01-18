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
import re
import subprocess

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

def patch_name(name2):

    name2 = name2.replace("rgb", "baseline")
    name2 = name2.replace("nosplitz", "no_splits")
    name2 = name2.replace("nightonly", "night_only")
    name2 = name2.replace("nosun", "no_sun")
    name2 = name2.replace("nobounce", "no_bounce")
    name2 = name2.replace("fixedsun", "fixed_sun")
    name2 = name2.replace("dayonly", "day_only")
    if "exposed" in name2:
        name2 = f"exposed({name2.replace('_exposed', '')})"
    if "histomatched" in name2:
        name2 = f"histo({name2.replace('_histomatched', '')})"
    if name2.endswith("cen"):
        name2 = "camera, r=" + re.sub("[^0-9]", "", name2)+"m"

    name2 = name2.replace("_", "\\_")

    return name2

def create_image_grid(root_directory):

    b  = "winsyn_riyal"
    d  = "winsyn_riyal_d"
    d4 = "winsyn_riyal_d4"
    e  = "winsyn_riyal_e"
    f  = "winsyn_riyal_f"
    g  = "winsyn_riyal_g"
    h  = "winsyn_riyal_h"

    with open(os.path.join("winsyn_riyal", "2048.txt"), "r") as fp: # read the splits for 'two'
        sa = fp.read().split("\n")[:-1]
    random.shuffle(sa)

    with open(os.path.join("winsyn_riyal_f", "2048.txt"), "r") as fp: # read the splits for 'two'
        sf = fp.read().split("\n")[:-1]
    random.shuffle(sf)

    with open(os.path.join("winsyn_riyal_h", "2048.txt"), "r") as fp: # read the splits for 'two'
        sh = fp.read().split("\n")[:-1]
    random.shuffle(sh)

    styles = [
        (b, "rgb", "png", sa, 32.587),
        (b, "labels", "png", sa, 6.481),
        # (b, "attribs", "txt"),
        (b, "rgb_exposed", "png", sa, 32.409),
        (b, "rgb_histomatched", "png", sa, 32.961 ),
        (b, "rgb_exposed_histomatched", "png", sa, 32.684 ),
        (b, "rgb_albedo", "png", sa, 16.948),
        (b, "diffuse", "png", sa, 22.364),
        (b, "phong_diffuse", "png", sa, 15.807 ),
        (b, "normals", "png", sa, 17.324),
        (b, "edges", "png", sa, 24.609),
        (b, "col_per_obj", "png", sa, 21.551),
        (b, "texture_rot", "png", sa, 26.647),
        (b, "voronoi_chaos", "png", sa, 19.300),
        # (b, "rgb_depth", "exr", sa, "na"),

        (d, "1spp", "png", sa, 7.231),
        (d, "2spp", "png", sa, 8.259),
        (d, "4spp", "png", sa, 10.499),
        (d, "8spp", "png", sa, 15.886),
        (d, "16spp", "png", sa, 20.81),
        (d, "32spp", "png", sa, 24.752),
        (d, "64spp", "png", sa, 26.224),
        (d, "128spp", "png", sa, 27.905),
        (d, "256spp", "png", sa, 28.939),
        (d, "512spp", "png", sa, 29.311),

        (d, "monomat", "png", sa, 19.771),
        (d, "nightonly", "png", sa, 27.240),
        (d, "nightonly_exposed", "png", sa, 30.891),
        (d, "nosun", "png", sa, 29.024),
        (d, "nosun_exposed", "png", sa, 28.972),
        (d, "nobounce", "png", sa, 30.083),
        (d, "nobounce_exposed", "png", sa, 30.535),
        (d, "fixedsun", "png", sa, 31.131),
        (d, "fixedsun_exposed", "png", sa, 31.91),
        (d, "dayonly", "png", sa, 32.240),
        (d, "dayonly_exposed", "png", sa, 31.965),

        (d4, "0cen", "png", sa, 30.328),
        (d4, "3cen", "png", sa, 32.624),
        (d4, "6cen", "png", sa, 32.763),
        (d4, "12cen", "png", sa, 33.092),
        (d4, "24cen", "png", sa, 32.545),
        (d4, "48cen", "png", sa, 30.184),
        (d4, "96cen", "png", sa, 29.77),

        (e, "lvl1", "png", sa, 5.104),
        (e, "lvl2", "png", sa, 12.221),
        (e, "lvl3", "png", sa, 16.881),
        (e, "lvl4", "png", sa, 23.728),
        (e, "lvl5", "png", sa, 25.422),
        (e, "lvl6", "png", sa, 28.476),
        (e, "lvl7", "png", sa, 29.977),
        (e, "lvl8", "png", sa, 32.396),
        (e, "lvl9", "png", sa, 33.805),

        (f, "no_rectangles", "png", sf, 30.345),
        (f, "only_squares", "png", sf, 30.628 ),
        (f, "nosplitz", "png", sf, 31.056),
        (f, "only_rectangles", "png", sf, 31.243),
        (f, "single_window", "png", sf, 31.744),
        (f, "wide_windows", "png", sf, 32.043),
        (f, "mono_profile", "png", sf, 32.196),

#        (g, "rgb", "png", sa, 0),
#        (g, "0monomat", "png", sa, 0),
#        (g, "0.33monomat", "png", sa, 0),
#        (g, "0.66monomat", "png", sa, 0),
#        (g, "1monomat", "png", sa, 0),
#        (g, "2monomat", "png", sa, 0),
#        (g, "4monomat", "png", sa, 0),
#        (g, "0multimat", "png", sa, 0),
#        (g, "0.33multimat", "png", sa, 0),
#        (g, "0.66multimat", "png", sa, 0),
#        (g, "1multimat", "png", sa, 0),
#        (g, "2multimat", "png", sa, 0),
#        (g, "4multimat", "png", sa, 0),
#        (g, "all_brick", "png", sa, 0),

        (h, "1nwall", "png", sh, 23.038),
        (h, "2nwall", "png", sh,  28.234),
        (h, "4nwall", "png", sh, 27.882),
        (h, "8nwall", "png", sh, 29.940),
        (h, "16nwall", "png", sh, 31.481),
        (h, "32nwall", "png", sh, 32.284),
        (h, "64nwall", "png", sh, 32.715),
        (h, "128nwall", "png", sh, 32.487)
    # (b, "canonical", "png"),
        # (b, "canonical_albedo", "png"),
        # (b, "canonical_transcol" "png")
    ]

    # with open(split_file, 'r') as f:
    #     splits = f.read().split("\n")

    # random.shuffle(splits)
    # splits = splits[:num]

    num = 1
    base_image_height = base_image_width = 128

    total_height = len(styles) * base_image_height
    total_width  = num * base_image_width

    grid_image = Image.new('RGB', (total_width, total_height))

    svg_out_dir = os.path.join(root_directory, f"svg_out_{time.time()}")
    os.makedirs(svg_out_dir, exist_ok=True)
    # draw = ImageDraw.Draw(grid_image)
    svg_out = svgwrite.Drawing(os.path.join(svg_out_dir, "labels_fid.svg"), profile='tiny')


    y_offset = 0

    for dataset, name, ext, splits, miou in styles:

        x_offset = 0
        svg_out.add(svg_out.text(f"{dataset}", insert=(x_offset, -1)))

        svg_out.add(svg_out.text(patch_name(name), insert=(int(x_offset - base_image_width), int ( y_offset + base_image_height / 2))))
        svg_out.add(svg_out.text(str(miou), insert=(int(x_offset * (num + 2)), int(y_offset + base_image_height / 2))))

        fid = subprocess.check_output(['python', '-m', 'pytorch_fid', '--device' ,'cuda:0',  f"/ibex/user/kellyt/windowz/{dataset}/{name}/", f"/ibex/user/kellyt/winsyn_89692_crops_512px_v1/all_fid.npz"])
        fid = float ( fid.decode('utf-8').replace("FID:", "").strip() )
        fid = '{0:.2f}'.format(fid)
        
        print(f" {dataset} {name}, {miou}, {fid}")
        svg_out.add(svg_out.text(str(fid), insert=(x_offset * (num + 2) + 100, y_offset + base_image_height / 2)))

        for split in splits[:num]:

            #print (f"{name}: {split}.{ext}")

            image_filef = os.path.join(os.path.join(root_directory, dataset, name, f"{split}.{ext}" ) )

            if ext.lower() in ['jpg', 'png', 'jpeg']:
                base_image = Image.open(image_filef)
            elif ext.lower() in ['exr']:
                base_image = rendr_depth_image(image_filef)
            elif ext.lower() in ['txt']:
                base_image = render_attribs(image_filef)

            base_image = base_image.resize((base_image_width, base_image_height)).convert('RGB')
            im_filename = f"{dataset}_{name}_{split}_{ext}.jpg"
            base_image.save(os.path.join(svg_out_dir, im_filename), format="JPEG")

            svg_out.add(svg_out.image(href=im_filename, insert=(x_offset, y_offset), size=(base_image_width, base_image_width)))

            grid_image.paste(base_image, (x_offset, y_offset))

            x_offset += base_image_width
        y_offset += base_image_width

        svg_out.save()
    output_path = os.path.join(root_directory, "image_grid.jpg")
    grid_image.save(output_path)


directory_path = '.'
create_image_grid(directory_path)
