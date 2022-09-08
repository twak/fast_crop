
import glob
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path
import re

def build_src_lookup(lookup_file, output_file):
    seen = {}
    with open(lookup_file, "r") as index_f:
        with open(output_file, "w") as output_f:
            lines = index_f.readlines()
            for i in range(int(len(lines) / 2)):
                img_line = lines[i * 2]
                crop_line = lines[i * 2 + 1].replace('"', '').strip()

                splits = img_line.split("[")
                src_file_name = splits[0]

                crop_region = splits[1].replace("]", "").strip()
                crop_region = [*map(lambda x: int(x.strip()), crop_region.split(","))]

                if os.path.exists(os.path.join ( r"C:\Users\twak\Downloads\windowz_1500_2", crop_line ) ) and crop_line not in seen:
                    output_f.write(img_line)
                    output_f.write(f'"{crop_line}"\n')
                    seen[crop_line] = True

src_lookup = build_src_lookup(
        r"C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\input_locations_second_1500.txt",
        r"C:\Users\twak\Documents\architecture_net\dataset\old_metadata_window_labels\from_labellers\input_locations_second_1500_exact.txt",
    )
