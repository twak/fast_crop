import os
import numpy as np
import matplotlib.cm as cm
from PIL import Image, ImageDraw
import itertools

def runs_of_ones(bits):
  for bit, group in itertools.groupby(bits):
    if bit: yield int ( sum(group) )

# load all greyscale label maps in a directory and create a per-class density image
def density_2d(dir):

    counts = np.zeros((10,512,512))
    hv = np.zeros((2,10,512))
    hvl = np.zeros((2,10,513))

    num = 10

    # create 10 512x512 numpy arrays
    for i in range(num):
        counts[i] = np.zeros((512,512))

    for j, file in enumerate( os.listdir(dir) ):
        print (f"{file} : {j}")
        if file.endswith(".png"):
            img = Image.open(os.path.join(dir, file))
            # convert image to numpy array
            img = np.array(img)
            # for each class, accumulate in counts
            for i in range(10):
                counts[i] += (img == i)

                v = (img[256] == i)
                h = (img[:,256] == i)

                hv[0][i] += v
                hv[1][i] += h

                for l in runs_of_ones(v):
                    hvl[0][i][l] += 1

                for l in runs_of_ones(h):
                    hvl[1][i][l] += 1

        # if j > 100:
        #     break


    for i in range(num):
        for j in range(2):
            # normalize to 0-1
            hvl[j][i] /= max ( 1, np.max(hvl[j][i]) )

    # create an image grid of counts
    grid = Image.new('RGB', (512*num, 512 * 5 ))
    for i in range(num):
        # convert counts to magma colormap

        counts[i] /= max ( 1, np.max(counts[i]) )
        magma = np.uint8(255 * cm.magma(counts[i]))
        grid.paste(Image.fromarray(magma), (512*i, 0))

        # add hv to grid in magma colormap

        hv[0][i] /= max ( 1, np.max(hv[0][i]) )
        hv[1][i] /= max ( 1, np.max(hv[1][i]) )

        # expand hv[0] and hv[1] to 512x512 in horizontal and vertical directions
        horizontal = np.repeat(hv[0][i], 512, axis=0).reshape(512,512)
        horizontal = horizontal.transpose()

        vertical = np.repeat(hv[1][i], 512, axis=0).reshape(512,512)

        grid.paste(Image.fromarray(np.uint8(255 * cm.magma(horizontal)) ), (512*i, 512))
        grid.paste(Image.fromarray(np.uint8(255 * cm.magma(vertical)) ), (512*i, 512*2))

        # create figure from runs_of_ones results
        for j in range(2):
            bg = Image.new('RGB', (512, 512))
            bgi = ImageDraw.Draw(bg)
            coords = []
            for x in range(512):
                if j == 0:
                    coords.append((x, 512 - (hvl[j][i][x])*512) )
                else:
                    coords.append(( (hvl[j][i][x])*512, x) )

            bgi.polygon(coords, fill="white", width=1)

            grid.paste(bg, (512*i, 512*3 + 512 * j))

    grid.save(os.path.join("/home/twak/Downloads", "density.png"))

    return counts

if __name__ == "__main__":
    density_2d("/home/twak/Downloads/winlab_5/labels")