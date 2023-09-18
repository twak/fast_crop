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

    bad = False

    for d, e in dirs:
        file = os.path.join(dataset_root, d, f"{base}.{e}")
        if e in ["png", "jpg"]:
            try:
                img = Image.open(file)
                img.verify()
            except Exception as x:
                print(x)
                img = None

            if img is None:
                bad = True
                print(f"failed to find and verify {d}//{base}.{e}!")
        elif not (os.path.exists(file) and os.path.getsize(file)):
            print(f"failed to find {d}//{base}.{e}!")
            bad = True

    if not bad:
        print(".", end="", flush=True)
        return 0 # good
    else:
        print(".")
        if len (sys.argv) > 2:
            print("deleting: " + str ( file ) )
            with contextlib.suppress(FileNotFoundError):
                for d, e in dirs:
                    file = os.path.join(dataset_root, d, f"{base}.{e}")
                    os.remove(file)
        else:
            print ( f"if this wasn't a dry run, I'd be removing: {base}" )

        return 1 # bad


def find_roots(files):
    out = {}
    for f in files:
        out[os.path.splitext(Path(f).name)[0]] = True

    return list ( out.keys() )


# dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"] ]
# dirs = [ ["rgb","png"], ["labels","png"], ["labels_8bit", "png"], ["exposed", "png"], ["attribs", "txt"] ]

dirs = \
    [["1024ms","png"], ["256ms","png"], ["attribs","txt"], ["canonical","png"], ["edges","png"], ["normals","png"],
     ["rgb_albedo","png"], ["texture_rot","png"], ["128ms","png"], ["512ms","png"], ["canonical","png"], ["col_per_obj","png"],
     ["labels","png"], ["phong_diffuse","png"], ["rgb_depth","exr"], ["voronoi_chaos","png"], ["2048ms","png"], ["64ms","png"],
     ["canonical_albedo","png"], ["diffuse","png"], ["labels_8bit","png"], ["rgb","png"], ["rgb_exposed","png"] ]


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
