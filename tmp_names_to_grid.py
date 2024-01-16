import sys
import glob
import time
import os
from PIL import Image

# for test only
#sys.argv += ['images/dot-*.png', 2, 3]

# get arguments
# pattern = sys.argv[1]
rows = 10 # int(sys.argv[2])
cols = 10 # int(sys.argv[3])

resolution = 256

# get filenames
filenames = [] # glob.glob(pattern)

dataset    = sys.argv[1]
split_file = sys.argv[2] # all.txt
o          = sys.argv[3] # folder - "labels"
ext        = sys.argv[4] # extension - "png"

sf = os.path.join (dataset, split_file)

if os.path.exists(sf):
    print(f"using split file {split_file}")
    with open( sf, "r") as f:
        for line in f:
            filenames.append( os.path.join (dataset, o, f"{line[:-1]}.{ext}") )
else:
    print ("split file not found: doing all.")
    for x in os.listdir(os.path.join(dataset, o)):
        if x.endswith(ext):
            filenames.append( os.path.join(dataset, o, x))

# filenames = filenames[-rows*cols:] # highest realism
filenames = filenames[:rows*cols] # lowest realism

# load images and resize to (100, 100)
images = [Image.open(name).resize((resolution, resolution)) for name in filenames]

# create empty image to put thumbnails
new_image = Image.new('RGB', (cols*resolution, rows*resolution))

# put thumbnails
i = 0
for y in range(rows):
    if i >= len(images):
        break
    y *= resolution
    for x in range(cols):
        x *= resolution
        img = images[i]
        new_image.paste(img, (x, y, x+resolution, y+resolution))
        print('paste:', x, y)
        i += 1

# save it
new_image.save(f'big_{o}_{time.time()}.jpg')
