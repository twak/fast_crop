import glob
import os
import sys
from pathlib import Path
import contextlib
import concurrent.futures

# if blender rendering is interupted, we may not have all data for each image. Delete those which aren't complete...
from PIL import Image

def valid_syn_pairs(base, dataset_root):

    global dirs
    files = []

    for d, e in dirs:
        files.append(os.path.join(dataset_root, d, f"{base}.{e}"))

    print (base)
    good = lambda f: os.path.exists(f) and os.path.getsize(f) > 0

    bad = False
    try:
        for d, e in dirs:
            file = os.path.join(dataset_root, d, f"{base}.{e}")
            if e in ["png", "jpg"]:
                img = Image.open(file)
                img.verify()
                if img is None:
                    bad = True
                    print(f"failed to verify {dataset_root}!")

            if not os.path.exists(file) and os.path.getsize(file):
                bad = True

    except:
        bad = True

    if not bad:
        return 0 # good
    else:
        for d, e in dirs:
            file = os.path.join(dataset_root, d, f"{base}.{e}")
            if not good(file):
                print(f"missing {d} -> {base}.{e}")

            if len (sys.argv) > 2:
                print("removing " + str ( file ) )
                with contextlib.suppress(FileNotFoundError):
                    os.remove(file)
            else:
                print ( "if this wasn't a dry run, I'd be removing " + file )

        return 1 # bad


def find_roots(files):
    out = {}
    for f in files:
        out[os.path.splitext(Path(f).name)[0]] = True

    return list ( out.keys() )


dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"] ]
#dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"], ["exposed", "png"], ["attribs", "txt"] ]

_pool = concurrent.futures.ThreadPoolExecutor()

roots = []

for d, e in dirs:
    roots.extend(glob.glob(os.path.join( sys.argv[1], d, "*."+e )))

roots = find_roots(roots)

processes = []
count = 0
for root in roots:

    processes.append(_pool.submit ( valid_syn_pairs, root, sys.argv[1] ))

    for r in concurrent.futures.as_completed(processes):
        count += r.result()

if len (sys.argv) > 2:
    print (f"have deleted {count}")
else:
    print(f"if this wasn't a dry run, I would have deleted {count}")
