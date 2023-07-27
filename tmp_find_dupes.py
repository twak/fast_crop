import os
from glob import glob
from pathlib import Path

for f in glob(r"C:\Users\twak\Documents\architecture_net\windows_part3\all_unzipped\*.json"):
    name = Path(f).name
    if not os.path.exists(fr"C:\Users\twak\Documents\architecture_net\windows_part3\all\{name}"):
        print(f"{name} missing")