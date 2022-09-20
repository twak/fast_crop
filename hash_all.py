import hashlib
import os
import sys
import time
from pathlib import Path

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def printt(message):
    terminal.write(message+"\n")
    log.write(message+"\n")

def walk (dirr, hash_loc, read_only = False):

    if not read_only:
        os.makedirs(hash_loc, exist_ok=True)

    printt (dirr)

    for f1 in os.listdir(dirr):
        full_path = os.path.join(dirr,f1)
        if os.path.isdir(full_path):
            if "metadata_hash" not in f1:
                walk(full_path, os.path.join (hash_loc, f1))
        else:
            hash_file = os.path.join(hash_loc,f1+".json")
            if os.path.exists(hash_file):
                try:
                    with open(hash_file, "r") as hash_json:
                        last_hash = hash_json.readline()
                        md5_string = md5(full_path)
                        if last_hash != md5_string:
                            printt(f"hash error {hash_file}")
                except:
                    printt(f"error reading hash {hash_file}")
            else:
                if not read_only:
                    with open(hash_file, "w") as hash_json:
                        md5_string = md5(full_path)
                        printt (f"new file. adding hash. {f1} : {md5_string}")
                        hash_json.write(md5_string)

    # for every hash file there should
    for f2 in os.listdir(hash_loc):
        if not os.path.isdir(os.path.join (hash_loc, f2)) and ".json" in f2:
            original_filename = os.path.join(dirr, f2[:-5])
            if not os.path.exists(original_filename):
                printt(f"hash exists for missing file {f2}")


print("starting hash run.")

hash_root = "./metadata_hashes"

read_only = len ( sys.argv ) == 1

terminal = sys.stdout
log = open(f"hash_result{int(time.time())}.log", "a")

for filename in os.listdir("."):
    if os.path.isdir(filename) and "metadata_hashes" not in filename and "metadata_website" not in filename:
        walk(os.path.join (".", filename), os.path.join (hash_root, filename), read_only)

print("hash run complete.")