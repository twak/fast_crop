import os, glob, shutil
from pathlib import Path

from PIL import Image

jpgs = []
jpgs.extend(glob.glob(r'.\*.JPG'))

for j in jpgs:
    with Image.open (j) as img:
        time = img._getexif()[36867]
        time = time.split()[0].replace(':','')

    file_name = Path(j).name
    file_name = os.path.splitext(file_name)[0]

    print (file_name)

    out_folder = f"michaela_vienna_{time}"
    out_folder = os.path.join(".", out_folder)
    os.makedirs(out_folder, exist_ok=True)

    shutil.move(j, os.path.join(out_folder, f"{file_name}.JPG"))
    shutil.move(f"{file_name}.NEF", os.path.join(out_folder, f"{file_name}.NEF"))

for f in os.listdir("."):
    if os.path.isdir(f):
        for g in os.listdir(f):
            if ".json" in g:
                out_folder = os.path.join ( "..", f )
                shutil.move ( os.path.join ( f, g ), os.path.joing ( out_folder, g ) )