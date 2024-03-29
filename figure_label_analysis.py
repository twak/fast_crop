import os
import numpy as np
import matplotlib.cm as cm
from PIL import Image, ImageDraw, ImageFont
import itertools
from matplotlib import font_manager
import time
from pathlib import Path

CLASSES = ["none", "window pane", "window frame", "open-window", "wall frame", "wall",
           # "door",
           "shutter", "blind", "bars", "balcony", "misc object"]

def runs_of_ones(bits):
  for bit, group in itertools.groupby(bits):
    if bit: yield int ( sum(group) )

# load all greyscale label maps in a directory and create a per-class density image
def density_2d(dir):

    num = len(CLASSES)

    simple = np.zeros((2,num))
    counts = np.zeros((num,512,512)) # 2D [class][pixels] accumulations
    hv = np.zeros((2,num,512)) # 1D [horizontal and vertical][class][pixels] accumulations
    hv_rl = np.zeros((2,num,52)) # 1D [horizontal and vertical][class][density] histogram of run lengths
    hv_o = np.zeros((2, num, 52))  # 1D [horizontal and vertical][class][density] histogram of last-first occurrences
    # hv_aspect = np.zeros((2, num, 52)) # 1D [horizontal and vertical][class][density] histogram of pseudo aspect ratios

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

                crs = cr.sum()
                simple[0, i] += crs
                if crs > 0:
                    simple[1, i] += 1

                counts[i] += cr

                v = cr.sum(axis=0)
                h = cr.sum(axis=1)

                hv[0][i] += v
                hv[1][i] += h


                # if crs > 0:
                #     a,b = cr[102:204,:].sum(), cr[308 : 410,:].sum()
                #     a_h = abs(a-b) / max(1,a+b)
                #     hv_aspect[0][i][int (a_h * 50 )] += 1
                #
                #     a,b = cr[:,102:204].sum(), cr[:,308 : 410].sum()
                #     a_v = abs(a-b) / max(1,a+b)
                #     hv_aspect[1][i][int (a_v * 50 )] += 1

                for hr in range(512):

                    for run, xx in [ (cr[hr], 0), (cr[:,hr], 1) ]:

                        # run = cr[hr]
                        for l in runs_of_ones(run):
                            hv_rl[xx][i][int (l / 10)] += 1

                        fl = np.nonzero(run)
                        if len(fl[0]) > 0:
                            length = fl[0][-1] - fl[0][0]
                        else:
                            length = 0
                        hv_o[xx][i][int (length / 10)] += 1

                        # run = cr[:,hr]
                        # for l in runs_of_ones(run):
                        #     hv_rl[1][i][int (l / 10)] += 1



                # for l in runs_of_ones(h):
                #     hv_rl[1][i][l] += 1

        # if j >= 100:
        #     break

    # save all arrays (aimple, hv...) to disk
    path = os.path.join(os.path.expanduser("~"), "Downloads", f"counts_{int (time.time() * 1000)}.npz" )
    np.savez(path,
            simple=simple,
            counts=counts,
            hv=hv,
            hv_rl=hv_rl,
            hv_o=hv_o
             )

    return path

def create_grid(dir):

    maps = np.load(dir)

    simple = maps["simple"]
    counts = maps["counts"]
    hv = maps["hv"]
    hv_rl = maps["hv_rl"]
    hv_o = maps["hv_o"]
    # hv_aspect = maps["hv_aspect"]

    num = len(CLASSES)

    # column max
    simple_max = np.max(simple, axis=1)

    for i in range(num):
        for x in range (52):
            hv_rl[0][i][x] *= x
            hv_rl[1][i][x] *= x

        div =  max ( 1, np.max(hv_rl[0][i]), np.max(hv_rl[1][i]) )
        hv_rl[0][i] /= div
        hv_rl[1][i] /= div

        # div = max (1, np.max(hv_aspect[0][i]), np.max(hv_aspect[1][i]))
        # hv_aspect[0][i] /= div
        # hv_aspect[1][i] /= div

        simple[0,i] /= simple_max[0]
        simple[1,i] /= simple_max[1]

    for i in range(1,num):
        for x in range (52):
            hv_o[0][i][x] *= x
            hv_o[1][i][x] *= x

    for i in range(1,num):
        div = max(1, np.max(hv_o[0][i][10:40]), np.max(hv_o[1][i][5:45]))
        hv_o[0][i] /= div
        hv_o[1][i] /= div

    # create an image grid of counts
    grid = Image.new('RGB', (512*num, 512 * 7 ))
    for i in range(num):
        # convert counts to magma colormap

        counts[i] /= max ( 1, np.max(counts[i]) )
        magma = np.uint8(255 * cm.magma(counts[i]))
        grid.paste(Image.fromarray(magma), (512*i, 512*2))

        # add hv to grid in magma colormap
        hv[0][i] /= max ( 1, np.max(hv[0][i]) )
        hv[1][i] /= max ( 1, np.max(hv[1][i]) )

        # expand hv[0] and hv[1] to 512x512 in horizontal and vertical directions
        horizontal = np.repeat(hv[0][i], 512, axis=0).reshape(512,512)
        horizontal = horizontal.transpose()

        vertical = np.repeat(hv[1][i], 512, axis=0).reshape(512,512)

        grid.paste(Image.fromarray(np.uint8(255 * cm.magma(horizontal)) ), (512*i, 512*3))
        grid.paste(Image.fromarray(np.uint8(255 * cm.magma(vertical)) ), (512*i, 512*4))

        # create a crappy bar graph from simple
        bg = Image.new('RGB', (512, 512))
        bgi = ImageDraw.Draw(bg)
        # c1 = np.uint8(255 * cm.magma([simple[0,i]]))[0]
        bgi.rectangle([(40, 511), (256, 511 - int (simple[0,i] * 512))], fill= tuple(np.uint8(255 * cm.magma([simple[0,i]]))[0]), outline="white" )
        bgi.rectangle([(256, 511), (471, 511 - int (simple[1,i] * 512))], fill= tuple(np.uint8(255 * cm.magma([simple[1,i]]))[0]), outline="white" )
        grid.paste(bg, (512*i, 512*0))

        for pos, histo in ((0,hv_rl), (1, hv_o ) ):

            # histrograms from runs_of_ones results
            bg = Image.new('RGB', (512, 512))
            bgi = ImageDraw.Draw(bg)

            purple, cream = "#fbfcbf", "#bb4d9f"

            bgi.line([(0, 512 - 400), (0, 512)], fill=purple, width=10)
            bgi.line([(0, 512), (400, 512)], fill=cream, width=10)

            for j, color in zip ( range(2), [cream, purple] ): # beige is vertical (1), purple is horizontal (0)

                coords = []

                for x in range(52):
                    coords.append((x*10, 512 - (histo[j][i][x])*512) )

                bgi.line(coords, fill=color, width=3)



            grid.paste(bg, (512 * i, 512 * (5 + pos)))

        bgi = ImageDraw.Draw(grid)
        font = font_manager.FontProperties(family='sans-serif', weight='bold')
        font = ImageFont.truetype(font_manager.findfont(font), 48)
        line =  f"{CLASSES[i]}"
        w, h = bgi.textsize(line, font=font)

        bgi.text(((512-w)/2 + 512 * i, 100 + 512), line, font=font, fill="white" )

    # grid.save("/home/twak/Documents/windowz_balcony_stats/syn_balcony.png" )

    grid.save( os.path.join(Path(dir).parent, f"grid.png"))
    # grid.save( os.path.join(Path(dir).parent, f"grid_{int (time.time() * 1000)}.png"))

    return counts

if __name__ == "__main__":

    path = density_2d(".")
    create_grid(path)
    # create_grid("/home/twak/Documents/windowz_balcony_stats/counts_1693924689181.npy.npz") #winlab5_counts_1693933123424.npy.npz")