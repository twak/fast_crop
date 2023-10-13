import shutil

'''
in which we translate from the post-submission mess into something the outside  world might understand.
'''

sixteen = [
    ([("winsyn_riyal", "labels_8bit", "png", "")],
    [("winsyn_riyal", "rgb", "png", "baseline color renders"),
    ("winsyn_riyal", "attribs", "txt", "baseline attributes")] )
]

two = [

    ([("winsyn_riyal", "labels_8bit", "png", "")],
    [
        ("winsyn_riyal", "rgb", "png", ""),
        ("winsyn_riyal", "rgb_exposed", "png", ""),
        ("winsyn_riyal", "rgb_albedo", "png", "render albedo channel"),
        ("winsyn_riyal", "normals", "png", "render normals"),
        ("winsyn_riyal", "voronoi_chaos", "png", "each object has a 3D voronoi pattern with a different scale. Voronoi cells have random colors."),
        ("winsyn_riyal", "col_per_obj", "png", "A different color on each object."),
        ("winsyn_riyal", "diffuse", "png", "A matte grey material on all objects."),
        ("winsyn_riyal", "edges", "png", "A sketch of the scene's edges."),
        ("winsyn_riyal", "texture_rot", "png", "A different rotated texted on each object."),
        ("winsyn_riyal", "phong_diffuse", "png", "")]),

    # different labels
    ([("winsyn_riyal_d", "labels_8bit", "png", "")],
    [
        ("winsyn_riyal_d", "monomat", "png", "All procedural materials replaced with a single one for each object-class. No variation in the procedural material."),
        ("winsyn_riyal_d", "nightonly", "png", ""),
        ("winsyn_riyal_d", "nightonly_exposed", "png", ""),
        ("winsyn_riyal_d", "nosun", "png", ""),
        ("winsyn_riyal_d", "nosun_exposed", "png", ""),
        ("winsyn_riyal_d", "nobounce", "png", ""),
        ("winsyn_riyal_d", "nobounce_exposed", "png", ""),
        ("winsyn_riyal_d", "fixedsun", "png", ""),
        ("winsyn_riyal_d", "fixedsun_exposed", "png", ""),
        ("winsyn_riyal_d", "dayonly", "png", ""),
        ("winsyn_riyal_d", "dayonly_exposed", "png", "")]),

    # circle radius tba
    ([
            ("winsyn_riyal_d4", "0cenlab_8bit", "png", ""),
            ("winsyn_riyal_d4", "3cenlab_8bit", "png", ""),
            ("winsyn_riyal_d4", "12cenlab_8bit", "png", ""),
            ("winsyn_riyal_d4", "24cenlab_8bit", "png", ""),
            ("winsyn_riyal_d4", "48cenlab_8bit", "png", ""),
            ("winsyn_riyal_d4", "96cenlab_8bit", "png", "")],
        [("winsyn_riyal_d4", "0cen", "png", ""),
        ("winsyn_riyal_d4", "3cen", "png", ""),
        ("winsyn_riyal_d4", "12cen", "png", ""),
        ("winsyn_riyal_d4", "24cen", "png", ""),
        ("winsyn_riyal_d4", "48cen", "png", ""),
        ("winsyn_riyal_d4", "96cen", "png", "")]),

    # label level
    ([
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", ""),
            ("winsyn_riyal_e", "lvl1_labels_8bit", "png", "")],
        [("winsyn_riyal_e", "lvl1", "png", ""),
        ("winsyn_riyal_e", "lvl2", "png", ""),
        ("winsyn_riyal_e", "lvl3", "png", ""),
        ("winsyn_riyal_e", "lvl4", "png", ""),
        ("winsyn_riyal_e", "lvl5", "png", ""),
        ("winsyn_riyal_e", "lvl6", "png", ""),
        ("winsyn_riyal_e", "lvl7", "png", ""),
        ("winsyn_riyal_e", "lvl8", "png", ""),
        ("winsyn_riyal_e", "lvl9", "png", "")] ) ]

two_f = [
    ([
            ("winsyn_riyal_f", "no_rectangles_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "only_squares_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "nosplitz_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "only_rectangles_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "single_window_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "wide_windows_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "mono_profile_labels_8bit", "png", "")],
        [("winsyn_riyal_f", "no_rectangles", "png", ""),
        ("winsyn_riyal_f", "only_squares", "png", ""),
        ("winsyn_riyal_f", "nosplitz", "png", ""),
        ("winsyn_riyal_f", "only_rectangles", "png", ""),
        ("winsyn_riyal_f", "single_window", "png", ""),
        ("winsyn_riyal_f", "wide_windows", "png", ""),
        ("winsyn_riyal_f", "mono_profile", "png", "")]),
]

import os
from PIL import Image


if __name__ == "__main__":

    out_dir = "riyal_jpg_v0"

    with open (os.path.join("winsyn_riyal",  "16384.txt"), "r" ) as fp:
        splits16 = fp.read().split("\n")[:-1]

    with open (os.path.join("winsyn_riyal",  "test.txt"), "r" ) as fp:
        splits16.extend ( fp.read().split("\n")[:-1] )

    with open(os.path.join("winsyn_riyal", "2048.txt"), "r") as fp: # read the splits for 'two'
        splits2 = fp.read().split("\n")[:-1]

    with open(os.path.join("winsyn_riyal_f", "2048.txt"), "r") as fp: # read the splits for 'two'
        splits2f = fp.read().split("\n")[:-1]

    i = 0

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "readme.txt"), "w") as re:
        for splits, z in [(splits16, sixteen), (splits2, two), (splits2f, two_f)]:
            for lbls, rgbs in z:
                re.write(f"{i}_lbl : \n")
                for root, folder, ext, desc in rgbs:
                    re.write(f"  {folder} (n={len(splits)})\n")
                    if len (lbls) == 1:
                        re.write(f"    labels : {lbls[0][1]}\n")
                    else:
                        re.write(f"    labels : {folder_labels}\n")

                i += 1


    i = 0
    count = 0

    for splits, z in [(splits16, sixteen), (splits2, two), (splits2f, two_f)]:
        for lbls, rgbs in z:

            lbl_folder = os.path.join(out_dir, f"{i}_lbl")

            os.makedirs(lbl_folder, exist_ok=True)
            with open(os.path.join(lbl_folder, "all.txt"), "w") as fp:
                for s in splits:
                    fp.write(f"{s}\n")

            for s in splits:

                count += 1

                for root, folder, ext, desc in rgbs:

                    path = os.path.join(root, folder, f"{s}.{ext}")

                    if not os.path.exists(path):
                        print(f"didn't find jpg {path}: {root} {folder} {ext}")
                        continue

                    dest = os.path.join(out_dir, lbl_folder, folder)
                    os.makedirs(dest, exist_ok=True)

                    if ext == "png":
                        im = Image.open(path)

                        # convert to rgb
                        im = im.convert("RGB")

                        im.save( os.path.join(dest, f"{s}.jpg"), format="JPEG", quality=90)
                    else: # txt and exr
                        shutil.copy(path, os.path.join ( dest, f"{s}.{ext}" ) )

                for root, folder, ext, desc in lbls: # no compression on the labels

                    path = os.path.join(root, folder, f"{s}.{ext}")

                    if not os.path.exists(path):
                        print(f"didn't find lbl {path}")
                        continue

                    dest = os.path.join(out_dir, lbl_folder, folder)
                    os.makedirs(dest, exist_ok=True)
                    shutil.copy(path, os.path.join ( dest, f"{s}.{ext}" ) )

            i += 1
            print(f"{count} files. {i} folders.")
