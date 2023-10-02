import os
import json
import numpy as np

def open_params(f):
    with open(f, 'r') as fp:
        txt = fp.read().split("\n")
        txt[-3] = txt[-3].replace(",", "")  # extra comma on final attribute

        return json.loads("".join(txt))

ma = 0
mx = 120000

max_attribs = 0
min_attribs = 1000000

things= [ "root/_rgb_render_time_ms",
    "root/_1spp_render_time_ms",
    "root/_2spp_render_time_ms",
    "root/_4spp_render_time_ms",
    "root/_8spp_render_time_ms",
    "root/_16spp_render_time_ms",
    "root/_32spp_render_time_ms",
    "root/_64spp_render_time_ms",
    "root/_128spp_render_time_ms",
    "root/_256spp_render_time_ms",
    "root/_512spp_render_time_ms" ]

tl = [[] for x in range ( len (things) )]

# geom, rgb, labels = [], [], []

bins=np.logspace(np.log10(0.1),np.log10(1.0), 50)

for f in os.listdir("/home/twak/Downloads/attribs_d"):
    attribs = open_params(f"/home/twak/Downloads/attribs_d/{f}")

    for i, a in  enumerate ( things ): #[(geom, "root/_geometry_generation_ms"), (rgb, "root/_rgb_render_time_ms"), (labels, "root/_labels_render_time_ms")]:

        if len(tl[i]) > 0:
            max_attribs = max(max_attribs, attribs[a])
            min_attribs = min(min_attribs, attribs[a])
        if a in attribs:
            tl[i].append(attribs[a])
            # if attribs[a] > mx:
            #     missed[n] += 1
            ma = max (ma, attribs[a])

hists = []
b2 = []

# create a histogram from geom using np
for i, g in enumerate(things): #  [geom, rgb, labels]:
    hist, bins = np.histogram( tl[i], bins=np.logspace(np.log10(300),np.log10(ma), 120), range=(0, mx), density=False)
    # hist, bins = np.histogram(geom, bins=120, range=(0, mx), density=False)
    hists.append(hist)
    b2.append(bins)

    print(f"{g} mean: {np.mean(tl[i])}")

# print (f"all-mean: {np.mean(geom + rgb + labels)}")
# print (f"{min_attribs} < attrib count < {max_attribs}")

for i in range ( len (hists[0]) ):
    print (b2[0][i], end=", ")
    for j in range (len(hists)):
        print (hists[j][i], end=", ")

    print()


