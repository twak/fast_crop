import sys
import glob
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

with open("/home/twak/Downloads/split.txt", "r") as f:
    for line in f:
        filenames.append(f"/home/twak/Downloads/winlab_4_png/holdout/{line[:-1]}.png")

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
new_image.save('realism_low.jpg')