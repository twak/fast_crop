import os
import sys
import glob
from pathlib import Path
import shutil

raw = sys.argv[1]
dest = sys.argv[2]
srcs = sys.argv[3:]

jpgs = []

for src in srcs:
    jpgs.extend(glob.glob( os.path.join (src, "*.JPG")) )
    if sys.platform != "win32":
        jpgs.extend(glob.glob( os.path.join (src, "*.jpg")) )

for jpg in jpgs:
    name, ext = os.path.splitext(Path(jpg).name)

    src_raw_path = os.path.join(Path(jpg).parent, name + "." + raw)

    extra = 0
    d_path = os.path.join(dest, f"{name}{ext}")
    dr_path = os.path.join(dest, f"{name}.{raw}")

    if os.path.exists(d_path):

        if os.path.getsize(d_path) == os.path.getsize(jpg):
            print (f"skipping duplicate (same sized) file {name}")
            continue

        while os.path.exists ( d_path ):
            extra +=1
            d_path  = os.path.join ( dest, f"{name}_{extra}{ext}" )
            dr_path = os.path.join ( dest, f"{name}_{extra}.{raw}")
            print (f"trying {Path(jpg).name} to {d_path} ")

    print (f"{extra} :: {name} ")

    shutil.copyfile(jpg, d_path)
    if os.path.exists (src_raw_path):
        shutil.copyfile(src_raw_path, dr_path)
    else:
        print ( f"missing raw {src_raw_path}" )