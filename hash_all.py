import hashlib
import os
import sys
from pathlib import Path

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def walk (dirr, hash_loc):

    os.makedirs(hash_loc, exist_ok=True)

    print (dirr)

    for filename in os.listdir(dirr):
        full_path = os.path.join(dirr,filename)
        if os.path.isdir(full_path):
            if "metadata_hash" not in filename:
                walk(full_path, os.path.join (hash_loc, filename))
        else:
            hash_file = os.path.join(hash_loc,filename+".json")
            if os.path.exists(hash_file):
                try:
                    with open(hash_file, "r") as hash_json:
                        last_hash = hash_json.readline()
                        md5_string = md5(full_path)
                        if last_hash != md5_string:
                            print(f"hash error {hash_file}", file=sys.stderr)
                except _:
                    print(f"error reading hash {hash_file}", file=sys.stderr)
            else:
                with open(hash_file, "w") as hash_json:
                    md5_string = md5(full_path)
                    print (f"new file. adding hash. {filename} : {md5_string}" ,file=sys.stderr)
                    hash_json.write(md5_string)

    # for every hash file there should
    for filename in os.listdir(hash_loc):
        if not os.path.isdir(os.path.join (hash_loc, filename)) and ".json" in filename:
            original_filename = os.path.join(dirr, filename[:-5])
            if not os.path.exists(original_filename):
                print(f"hash exists for missing file {filename}", file=sys.stderr)


hash_root = "./metadata_hashes"

for filename in os.listdir("."):
    if os.path.isdir(filename) and "metadata_hashes" not in filename and "metadata_website" not in filename:
        walk(os.path.join (".", filename), os.path.join (hash_root, filename))
