import glob
import os
import sys

import process_labels
from PIL import Image
import numpy as np
import concurrent.futures

from pathlib import Path

# convert labels in PRETTY colours (or PRETTY_FILMIC...) to greyscale 8 bits for mmseg

def to_greyscale_labels(png_file, out_folder):

    print (png_file)
    output_path = os.path.join(out_folder, os.path.basename(Path(png_file).name) )
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return # already done, skip

    pretty = Image.open(png_file, "r")
    label = np.asarray ( pretty )[:,:,0:3]

    tol = 10

    pretty_map = process_labels.colours_for_mode(process_labels.PRETTY)
    output = np.zeros(pretty.size, dtype=int)

    for i, label_name in enumerate (process_labels.LABEL_SEQ_NO_DOOR):

        colour = np.array ( pretty_map[label_name] )
        equality = np.logical_and ( np.greater(label, colour-tol), np.less(label, colour+tol) )
        class_map = np.all(equality, axis=-1)
#        print (f"{label_name} - {colour} :: {class_map.sum()}")
        output = output * (1- class_map) # zero out any previous labels
        output = output + class_map * i  # set greyscale label

    print ("saving to %s"%output_path)
    Image.fromarray(np.uint8(output)).save( output_path )

def to_color_labels(png_file, out_folder):

    print(png_file)
    output_path = os.path.join(out_folder, os.path.basename(Path(png_file).name))
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return  # already done, skip

    grey = Image.open(png_file, "r")
    label = np.asarray(grey)#[:, :, 0:3]
    color_seg = np.zeros((grey.size[0], grey.size[1], 3), dtype=np.uint8)

    for i, l_name in enumerate ( process_labels.LABEL_SEQ_NO_DOOR ):
        color = process_labels.colours_for_mode(process_labels.PRETTY)[l_name]
        color_seg[i == label, :] = color

    print("saving to %s" % output_path)
    Image.fromarray(color_seg).save(output_path)
    # Image.fromarray(np.uint8(color_seg)).save(output_path)


if __name__ == "__main__":

    _pool = concurrent.futures.ThreadPoolExecutor(max_workers=16)

    labels = []

    src_folder = sys.argv[2] # eg labels
    dest_folder = sys.argv[3] # eg labels_8bit

    labels.extend(glob.glob(os.path.join( sys.argv[1], src_folder, "*.png")))

    if True: # rgb to greyscale
        out_dir = os.path.join(sys.argv[1], dest_folder)
        fn = to_greyscale_labels

    # else: # greyscale to rgb fi me
    #     fn = to_color_labels
    #     out_dir = os.path.join(sys.argv[1], "labels_pretty")

    os.makedirs(out_dir, exist_ok=True)

    for lab in labels:
        fn (lab, out_dir )
        _pool.submit ( fn, lab, out_dir, )
