import os
import sys
import glob
from pathlib import Path
import shutil

raw = sys.argv[1]
src = sys.argv[2]
dest = sys.argv[3]


jpgs = []
jpgs.extend(glob.glob( os.path.join (src, "*.JPG")) )
if sys.platform != "win32":
    jpgs.extend(glob.glob( os.path.join (src, "*.jpg")) )

for jpg in jpgs:
    name, ext = os.path.splitext(Path(jpg).name)
    # name = x[0]
    # ext = x[1]
    raw_file = os.path.join ( Path(jpg).parent, name +"."+ raw)

    extra = 0
    d_path = os.path.join( dest, f"{name}{ext}" )
    while os.path.exists ( d_path ):
        extra +=1
        d_path = os.path.join ( dest, f"{name}_{extra}{ext}" )
        print (f"trying {Path(jpg).name} to {d_path} ")

    shutil.copyfile(jpg, d_path)
    if os.path.exists (raw_file):
        shutil.copyfile(raw_file, os.path.join ( dest, f"{name}_{extra}.{raw}" ))
    else:
        print ( f"missing raw {name}.{raw}" )