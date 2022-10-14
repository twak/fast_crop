import glob
import os
from pathlib import Path
from random import shuffle
import shutil


def split(rgb_files, output_folder, label_names=[["labels", "png"]], output_split=[[50, "val"], [50, "test"]] ):


    shuffle(rgb_files)

    cum_perc = []
    total = 0
    for p, n in output_split:
        total += p
        cum_perc.append([ int ( total * len (rgb_files) / 100 ) , p, n])

    if total != 100:
        print("error, percents don't add up!")
        return

    cpi = 0
    for i, rgb in enumerate ( rgb_files ):
        print (f"copying {i} {rgb}")

        tpn = cum_perc[cpi]
        out_stub = os.path.join(output_folder, tpn[2])
        prgb = Path(rgb)

        os.makedirs(os.path.join( out_stub, prgb.parent.name), exist_ok=True )
        shutil.copyfile(rgb, os.path.join( out_stub, prgb.parent.name, prgb.name ))
        basename = os.path.splitext(prgb.name)[0]

        for name, extn in label_names:
            src = prgb.parent.parent.joinpath(name).joinpath(basename+"."+extn)
            if not os.path.exists(src):
                print (f"missing {name} for {rgb}")
            os.makedirs(os.path.join(out_stub, name), exist_ok=True)
            shutil.copyfile( src, os.path.join(out_stub, name, basename+"."+extn ) )

        while i > cum_perc[cpi][0]: # cumulative > i
            cpi += 1

rgbs = []
rgbs.extend(glob.glob(os.path.join( r"/home/twak/Downloads/winlab_1/rgb", "*.jpg")))
split ( rgbs, r"/home/twak/Downloads//winlab_2",
        label_names=[["labels", "png"]],
        output_split=[[50, "val"], [50, "test"]] )