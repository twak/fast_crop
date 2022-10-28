import glob
import os
import pathlib, json

from pathlib import Path
from platform import platform


def count(dataset_root, label_json_files):
    '''
    How many have we had labelled?...
    '''

    total = 0
    total_json_files = 0
    FREQ = [0,0,0,0,0,0]
    bybatch={}

    for json_file in label_json_files:

        batch = Path ( json_file ).parent.name

        with open(json_file, "r") as f:
            data = json.load(f)
            total_json_files += 1

            wins = len (data.items())

            # print(f"counting crops from {json_file} = {wins}")
            FREQ[wins] += wins
            total += wins

            if batch in bybatch:
                bybatch[batch]+= wins
            else:
                bybatch[batch] = wins

    print (f"total {total} in {total_json_files} files")

    for i in range ( len (FREQ) ):
        print (f"{i} : {FREQ[i]}")

    print("\n\n label counts")

    for a, b in bybatch.items():
        print(f"{a}, {b}")

def count_photos (jpg_files):

    bybatch = {}

    for photo in jpg_files:

        batch = Path(photo).parent.name

        if batch in bybatch:
            bybatch[batch] += 1
        else:
            bybatch[batch] = 1

    print ("\n\nphoto counts")
    for a, b in bybatch.items():
        print(f"{a}, {b}")


if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\dataset"
    else:
        dataset_root = r"/mnt/vision/data/archinet/data"

    json_src = []
    json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "*", "*.json")))

    count (dataset_root, json_src)
    # count_photos(photos)