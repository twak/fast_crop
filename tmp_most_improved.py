import os
from PIL import Image

real = "/home/twak/Documents/cherrypicked_test/winlab"
syn = "/home/twak/Documents/cherrypicked_test/riyal"

real_mious = {}
real_files = {}

countries = {}

all_countries = ["austria", "uk", "other", "usa", "egypt", "germany", "other"]

for country in all_countries:
    with open(f"/home/twak/Downloads/winlab_5/{country}.txt") as fp:
        countries[country] = set([x.rstrip() for x in fp])


for f in os.listdir(real):

    miou, name = f[:-4].split("-")
    real_miou = float(miou)

    real_mious[name] = miou
    real_files[name] = f

for f in os.listdir(syn):

    miou, name = f[:-4].split("-")
    syn_miou = float(miou)

    real_miou = float ( real_mious[name] )

    for c, ids in countries.items():
        if name in ids:
            country = c

    print (f"{syn_miou}, {real_miou}, {country}")

    # real_image = Image.open(os.path.join(real, real_files[name]))
    # syn_image = Image.open(os.path.join(syn, f))
    # gts = Image.open(os.path.join ("/home/twak/Downloads/cherrypicked_test/both", f"{name}.jpg") )
    #
    # composite = Image.new('RGB', (512, 512*4))
    # composite.paste(gts, (0, 0))
    # composite.paste(real_image, (0, 512 * 2))
    # composite.paste(syn_image, (0, 512 * 3))
    #
    # delta = real_miou - syn_miou
    #
    # composite.save(f"/home/twak/Downloads/cherrypicked_test/syn_tmp/%.2f_%.2f_%.2f_%s.jpg" % (syn_miou, delta, real_miou, name) )
    #
