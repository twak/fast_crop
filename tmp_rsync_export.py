import os
import process_labels
from pathlib import Path
import json

if __name__ == "__main__":

    with open("./tomove.txt", "w") as togo:

        for batch in ["yuan_dalian_20230323"]:#os.listdir("data/photos"):
            # if is dir
            if os.path.isdir(os.path.join("data/photos", batch)):
                for file in os.listdir(f"data/photos/{batch}"):
                    if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):

                        im_file = os.path.join("data/photos", batch, file)
                        out_name, out_ext = os.path.splitext(os.path.basename(im_file))

                        json_file = Path(im_file).parent.parent.parent.joinpath("metadata_single_elements").joinpath(batch).joinpath(f"{out_name}.json")

                        if os.path.exists(os.path.join(".", json_file)):  # there is a crop file

                            prev = json.load(open(json_file, "r"))
                            rects = prev["rects"]

                            tags = []

                            if "tags" in prev:
                                tags = prev["tags"]

                            if 'deleted' in tags:
                                print(f"skipping deleted {im_file}")
                                continue

                            print(f"{im_file}")
                            togo.write(f"data/photos/{batch}/{file}\n")

                            for extension in process_labels.RAW_EXTS:
                                if Path(im_file).with_suffix("." + extension).exists():
                                    togo.write(f"data/photos/{batch}/{out_name}.{extension}\n")


