from PIL import Image, ImageDraw
import os
import fnmatch
import numpy as np
import imageio
import cv2
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
import json

def grey_to_color(grey):

    label = np.asarray(grey)#[:, :, 0:3]
    color_seg = np.zeros((grey.size[0], grey.size[1], 3), dtype=np.uint8)

    for i, l_name in enumerate ( process_labels.LABEL_SEQ_NO_DOOR ):
        color = process_labels.colours_for_mode(process_labels.PRETTY)[l_name]
        color_seg[i == label, :] = color

    return Image.fromarray(color_seg)


def create_image_grid(num, root_directory, split, *styles):

    base_image_width = 512  # Adjust this to your desired width
    base_image_height = 512  # Adjust this to your desired height

    total_width = len(styles) * base_image_width
    total_height = num * base_image_height

    grid_image = Image.new('RGB', (total_width, total_height))
    # draw = ImageDraw.Draw(grid_image)

    # read lines from split file
    with open(split, "r") as f:
        lines = f.readlines()
        for i, x in enumerate ( lines ):

            for j, s in enumerate ( styles ):
                dir = os.path.join(root_directory, s[0])
                image_file = os.path.join(dir, x[:-1] + "." + s[1])
                image = Image.open(image_file)

                if s[0] == "labels":
                    image = grey_to_color(image)

                grid_image.paste(image, (j * base_image_width, i * base_image_height))


            if i > num:
                break


    output_path = os.path.join(root_directory, "lab2lab_grid.jpg")
    grid_image.save(output_path)



# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
create_image_grid(20, directory_path, os.path.join(directory_path, "test.txt"), ("rgb", "jpg"), ("labels", "png"), ("labels_predicted_1", "png"), ("labels_l2l_1", "png") )