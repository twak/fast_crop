import os
import process_labels
from pathlib import Path
import json

if __name__ == "__main__":

    for batch in os.listdir("data/photos"):
        # if is dir
        if os.path.isdir(os.path.join("data/photos", batch)):
            for file in os.listdir(f"data/photos/{batch}"):
                ext = os.path.splitext(file)[1]
                if ext.lower() in process_labels.RAW_EXTS:
                    for jext in ["jpg", "JPG", "jpeg", "JPEG"]:
                        if not Path(os.path.join("data/photos", batch, file)).with_suffix("." + jext).exists():
                            print (f"data/photos/{batch}/{file}")
                            break