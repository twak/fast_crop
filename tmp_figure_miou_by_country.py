import os
from PIL import Image
import matplotlib.pyplot as plt
import  numpy as np

import process_labels

real = "/home/twak/Documents/cherrypicked_test/winlab"
syn = "/home/twak/Documents/cherrypicked_test/riyal"

real_mious = {}
real_files = {}

countries = {}

all_countries = ["austria", "uk", "other", "usa", "egypt", "germany"]

coords = {}

for country in all_countries:
    with open(f"/home/twak/Downloads/winlab_5/{country}.txt") as fp:
        countries[country] = set([x.rstrip() for x in fp])
    coords[country] = ([],[])

labels = []
for i in process_labels.LABEL_SEQ_NO_DOOR:
    labels.append([ [], [] ])

for f in os.listdir(real):

    miou, name = f[:-4].split("-")
    real_miou = float(miou)

    real_mious[name] = miou
    real_files[name] = f

count = 0

for f in os.listdir(syn):

    count += 1

    miou, name = f[:-4].split("-")
    syn_miou = float(miou)
    real_miou = float ( real_mious[name] )

    for c, ids in countries.items():
        if name in ids:
            country = c

    coords[country][0].append(syn_miou)
    coords[country][1].append(real_miou)

    label_file = f"/home/twak/Downloads/winlab_5/labels/{name}.png"

    im = Image.open(label_file)
    npa = np.array(im)
    has_label = []
    number_labels=0

    for i in range (11):
        has_label = (npa == i).sum() > 0
        if has_label:
            labels[i][0].append( syn_miou )
            labels[i][1].append( real_miou )
            number_labels += 1

    print(f"{syn_miou}, {real_miou}, {country}, {number_labels}, {os.path.getsize(label_file)}")


    # if count > 100:
    #     break



if True: # per-regiion scatter
    fig, axs = plt.subplots(6, 3, figsize=(16,30))

    for color, country, i in zip (["red", "green", "blue", "orange", "purple", "cyan", "magenta"], countries, [x for x in range(len(countries))]):
        ax = axs.flat[i]
        ax.scatter(coords[country][0], coords[country][1], 18, color=color ,  edgecolors='none',  alpha=0.2 )
        ax.set_title(country)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 100])

    start = len (countries)
    for i, label in enumerate (process_labels.LABEL_SEQ_NO_DOOR):

        ax = axs.flat[i + start]
        ax.scatter(labels[i][0], labels[i][1], 18, color="black" ,  edgecolors='none',  alpha=0.2 )

        ax.set_title(label)
        ax.set_xlim([0, 100])
        ax.set_ylim([0, 100])



    fig.suptitle('mIoU per-sample (horizontal/vertical:synthetic/real trained network; n=4096). Eval on real.')
    fig.show()
