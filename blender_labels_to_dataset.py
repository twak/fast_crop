import glob
import os
import process_labels
from PIL import Image
import numpy as np

from pathlib import Path

def to_greyscale_labels(png_file, out_folder):

    print (png_file)

    pretty = Image.open(png_file, "r")
    label = np.asarray ( pretty )[:,:,0:3]

    tol = 10

    pretty_map = process_labels.colours_for_mode(process_labels.PRETTY_FILMIC)
    output = np.zeros(pretty.size, dtype=int)

    for i, label_name in enumerate (process_labels.LABEL_SEQ):

        colour = np.array ( pretty_map[label_name] )
        equality = np.logical_and ( np.greater(label, colour-tol), np.less(label, colour+tol) )
        class_map = np.all(equality, axis=-1)
        print (f"{label_name} - {colour} :: {class_map.sum()}")
        output = output * (1- class_map) # zero out any previous labels
        output = output + class_map * i  # set greyscale label

    Image.fromarray(np.uint8(output)).save(os.path.join(out_folder, os.path.basename(Path(png_file).name) ) )


labels = []
# json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
labels.extend(glob.glob(os.path.join( r"C:\Users\twak\Downloads\blender_dataset_test", "labels_pretty", "**.png")))


for lab in labels:
    to_greyscale_labels(lab, r"C:\Users\twak\Downloads\blender_dataset_test\labels" )