import os
import numpy as np
import matplotlib.cm as cm
from PIL import Image, ImageDraw, ImageFont
import itertools
from matplotlib import font_manager

CLASSES = ["none", "window pane", "window frame", "open-window", "wall frame", "wall", "shutter", "blind", "bars", "balcony", "misc object"]

def runs_of_ones(bits):
  for bit, group in itertools.groupby(bits):
    if bit: yield int ( sum(group) )

# load all greyscale label maps in a directory and create a per-class density image
def density_2d(dir):

    num = len(CLASSES)

    simple = np.zeros((num))
    counts = np.zeros((num,512,512)) # 2D [class][pixels] accumulations
    hv = np.zeros((2,num,512)) # 1D [horizontal and vertical][class][pixels] accumulations
    hvl = np.zeros((2,num,52)) # 1D [horizontal and vertical][class][density] histogram of run lengths


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
            for i in range(num):

                cr = (img == i)

                simple[i] += cr.sum()
                counts[i] += cr

                v = cr.sum(axis=0)
                h = cr.sum(axis=1)

                hv[0][i] += v
                hv[1][i] += h

                for hr in range(512):
                    run = cr[hr]
                    for l in runs_of_ones(run):
                        hvl[0][i][int (l / 10)] += 1

                for hr in range(512):
                    run = cr[:,hr]
                    for l in runs_of_ones(run):
                        hvl[1][i][int (l / 10)] += 1

                # for l in runs_of_ones(h):
                #     hvl[1][i][l] += 1

        # if j >= 1 :
        #     break

    simple_max = simple.max()
    for i in range(num):
        div =  max ( 1, np.max(hvl[0][i]), np.max(hvl[1][i]) )
        hvl[0][i] /= div
        hvl[1][i] /= div
        simple[i] /= simple_max

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

        # create a crappy bar graph from simple
        bg = Image.new('RGB', (512, 512))
        bgi = ImageDraw.Draw(bg)
        color = np.uint8(255 * cm.magma([simple[i]]))[0]
        bgi.rectangle([(0, 511), (511, 511 - int (simple[i] * 512))], fill= tuple(color), outline="white" )
        grid.paste(bg, (512*i, 512*4))

        # histrograms from runs_of_ones results
        bg = Image.new('RGB', (512, 512))
        bgi = ImageDraw.Draw(bg)

        for j, color in zip ( range(2), ["#992d7f", "#fbfcbf"] ):

            coords = []

            for x in range(52):
                coords.append((x*10, 512 - (hvl[j][i][x])*512) )

            bgi.line(coords, fill=color, width=4)

        font = font_manager.FontProperties(family='sans-serif', weight='bold')
        font = ImageFont.truetype(font_manager.findfont(font), 48)
        line =  f"{CLASSES[i]}"
        w, h = bgi.textsize(line, font=font)

        bgi.text((500-w, 20), line, font=font, fill="white" )
        grid.paste(bg, (512*i, 512*3))

    grid.save(os.path.join("/home/twak/Downloads", "density.png"))

    return counts

if __name__ == "__main__":
    density_2d("/home/twak/Downloads/winlab_5/labels")