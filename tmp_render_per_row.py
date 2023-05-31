import sys
import glob
import time
import os
from PIL import Image

# for test only
#sys.argv += ['images/dot-*.png', 2, 3]

# get arguments
# pattern = sys.argv[1]
rows = 100 # int(sys.argv[2])
folders = ["rgb", "albedo", "exposed", "labels"]
cols = len(folders) # int(sys.argv[3])

resolution = 256

# get filenames
filenames = [] # glob.glob(pattern)

dataset = sys.argv[1]
split_file = sys.argv[2] # "/home/twak/Downloads/split.txt"

with open( os.path.join (dataset, split_file), "r") as f:
    for line in f:
        filenames.append( os.path.join (f"{line[:-1]}.png") )

# create empty image to put thumbnails
new_image = Image.new('RGB', (cols*resolution, rows*resolution))

i = 0
for y in range(rows):

    if i >= len(filenames):
        break
    y *= resolution
    for x in range(cols):
        print(f"{y} + {x} : {filenames[y]} + {folders[x]}")
        img = Image.open(os.path.join(dataset, folders[x], filenames[y] ) )
        img = img.resize((resolution, resolution))
        x *= resolution
        new_image.paste(img, (x, y, x+resolution, y+resolution))
        print('paste:', x, y)
        i += 1

# save it
new_image.save(f'grid_{time.time()}.jpg')