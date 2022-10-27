import glob
import os
import process_labels
from PIL import Image
import numpy as np
import concurrent.futures

from pathlib import Path

def to_greyscale_labels(png_file, out_folder):

    print (png_file)
    output_path = os.path.join(out_folder, os.path.basename(Path(png_file).name) )
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return # already done, skip

    pretty = Image.open(png_file, "r")
    label = np.asarray ( pretty )[:,:,0:3]

    tol = 10

    pretty_map = process_labels.colours_for_mode(process_labels.PRETTY_FILMIC)
    output = np.zeros(pretty.size, dtype=int)

    for i, label_name in enumerate (process_labels.LABEL_SEQ):

        colour = np.array ( pretty_map[label_name] )
        equality = np.logical_and ( np.greater(label, colour-tol), np.less(label, colour+tol) )
        class_map = np.all(equality, axis=-1)
#        print (f"{label_name} - {colour} :: {class_map.sum()}")
        output = output * (1- class_map) # zero out any previous labels
        output = output + class_map * i  # set greyscale label

    print ("saving to %s"%output_path)
    Image.fromarray(np.uint8(output)).save( output_path )


_pool = concurrent.futures.ThreadPoolExecutor()

labels = []

labels.extend(glob.glob(os.path.join( r"/ibex/scratch/kellyt/windowz/winsyn_king/", "labels", "*.png")))


out_dir = r"/ibex/scratch/kellyt/windowz/winsyn_king/labels_8bit"
os.path.makedirs(out_dir, exit_okay=True)

for lab in labels:
    _pool.submit ( to_greyscale_labels, lab, out_dir, )
