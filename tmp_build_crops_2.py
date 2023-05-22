import glob

import single_one_off_import_lyd_json
from pathlib import Path
from sys import platform
import os
import shutil
from collections import defaultdict
import json

if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\windows_part3"
    else:
        dataset_root = r"/mnt/vision/data/archinet/data"

    src_lookup = single_one_off_import_lyd_json.build_src_lookup(
        [r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_3.txt",
         r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_4.txt",
         r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_5.txt",
         r"C:\Users\twak\Documents\architecture_net\windows_part3\log_part_6.txt"])

    images = []
    images.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\windows_part3\crops\**.jpg'))

    if False:
        # create placeholder files for everything we sent to the labellers so far
        for i in images:
            src_info = src_lookup[Path(i).name]
            # print (src_info['src'])
            out = os.path.join (dataset_root, "metadata_window_labels_2", Path ( src_info['src'] ).with_suffix(".json") )
            os.makedirs(Path(out).parent, exist_ok=True)
            with open(out, 'w') as _:
                pass

    if True:
        # these are the files in our format, but need moving to correct batch folder
        for i in glob.glob(r'C:\Users\twak\Documents\architecture_net\windows_part3\labels_all_labels_so_far\*.json'):
            src_info = src_lookup[Path(i).with_suffix(".jpg").name]
            out = os.path.join( dataset_root, "metadata_window_labels_2", Path(src_info['src']).with_suffix(".json") )
            print(src_info['src'])
            os.makedirs(Path(out).parent, exist_ok=True)
            shutil.copyfile(i, out)

    if False:
        # count labels for both sets:

        count = defaultdict(lambda: 0)

        for one in glob.glob (r"C:\Users\twak\Documents\architecture_net\windows_part3\metadata_window_labels\*\**.json"):
            with open(one, "r") as f:
                data = json.load(f)
            count[Path(one).parent.name] += len ( data.items() )


        for name, value in count.items():
            print (f"{name} , {value} " )

        print(f"\n  n={sum(count.values()) } \n")

        for two in glob.glob (r"C:\Users\twak\Documents\architecture_net\windows_part3\metadata_window_labels_2\*\**.json"):
            if os.path.getsize(two) == 0:
                size = 1
            else:
                with open(two, "r") as f:
                    data = json.load(f)
                    size = len ( data.items() )

            count[Path(two).parent.name] += size


        for name, value in count.items():
            print (f"{name} , {value} " )


        print(f"\n  n2={sum(count.values()) } \n")