import os, glob, shutil
from pathlib import Path

from PIL import Image


# move each file to a folder named for date taken
#
# jpgs = []
# jpgs.extend(glob.glob(r'.\*.JPG'))
# for j in jpgs:
#     with Image.open (j) as img:
#         time = img._getexif()[36867] # date
#         time = time.split()[0].replace(':','')
#
#     file_name = Path(j).name
#     file_name = os.path.splitext(file_name)[0]
#
#     print (file_name)
#
#     out_folder = f"michaela_vienna_{time}"
#     out_folder = os.path.join(".", out_folder)
#     os.makedirs(out_folder, exist_ok=True)
#
#     shutil.move(j, os.path.join(out_folder, f"{file_name}.JPG"))
#     shutil.move(f"{file_name}.NEF", os.path.join(out_folder, f"{file_name}.NEF"))

# and do the json files
for f in os.listdir("."):
    if os.path.isdir(f):
        print (f"dir {f}")
        for g in os.listdir(f):
            if ".JPG" in g:
                name = os.path.splitext(g)[0]
                if not os.path.exists( os.path.joing(f, f"{name}.json") ):
                    print (f"**** missing json was {g}/{name}")
            if ".json" in g:
                out_folder = os.path.join ( "..", "florian_jsons", f )
                os.makedirs ( out_folder, exist_ok=True)
                shutil.move ( os.path.join ( f, g ), os.path.joing ( out_folder, g ) )