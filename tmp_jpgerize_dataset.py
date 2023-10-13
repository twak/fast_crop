import shutil

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
        ("winsyn_riyal_d", "night_only", "png", ""),
        ("winsyn_riyal_d", "night_only_exposed", "png", ""),
        ("winsyn_riyal_d", "no_sun", "png", ""),
        ("winsyn_riyal_d", "no_sun_exposed", "png", ""),
        ("winsyn_riyal_d", "no_sun", "png", ""),
        ("winsyn_riyal_d", "no_sun_exposed", "png", ""),
        ("winsyn_riyal_d", "no_bounce", "png", ""),
        ("winsyn_riyal_d", "no_bounce_exposed", "png", ""),
        ("winsyn_riyal_d", "fixed_sun", "png", ""),
        ("winsyn_riyal_d", "fixed_sun_exposed", "png", ""),
        ("winsyn_riyal_d", "day_only", "png", ""),
        ("winsyn_riyal_d", "day_only_exposed", "png", "")]),

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
        ("winsyn_riyal_e", "lvl9", "png", "")] ),

    ([
            ("winsyn_riyal_f", "no_rectangles_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "only_squares_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "no_splits_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "only_rectangles_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "single_window_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "wide_windows_labels_8bit", "png", ""),
            ("winsyn_riyal_f", "mono_profile_labels_8bit", "png", "")],
        [("winsyn_riyal_f", "no_rectangles", "png", ""),
        ("winsyn_riyal_f", "only_squares", "png", ""),
        ("winsyn_riyal_f", "no_splits", "png", ""),
        ("winsyn_riyal_f", "only_rectangles", "png", ""),
        ("winsyn_riyal_f", "single_window", "png", ""),
        ("winsyn_riyal_f", "wide_windows", "png", ""),
        ("winsyn_riyal_f", "mono_profile", "png", "")]),
]

import os
from PIL import Image


if __name__ == "__main__":

    out_dir = "riyal_jpg"

    with open (os.path.join("winsyn_riyal",  "16384.txt"), "r" ) as fp:
        splits16 = fp.read().split("\n")

    with open (os.path.join("winsyn_riyal",  "test.txt"), "r" ) as fp:
        splits16.append ( fp.read().split("\n") )

    with open(os.path.join("winsyn_riyal", "2048.txt"), "r") as fp: # read the splits for 'two'
        splits2 = fp.read().split("\n")

    i = 0
    count = 0
    for splits, z in [(splits16, sixteen), (splits2, two)]:
        for lbls, rgbs in z:

            for s in splits:

                lbl_folder = os.path.join(out_dir, f"{i}_lbl")
                count += 1


                for root, folder, ext, desc in rgbs:

                    path = os.path.join(root, folder, f"{s}.{ext}")

                    if not os.path.exists(path):
                        print(f"didn't find jpg {path}")

                    # dest = os.path.join(out_dir, lbl_folder, folder)
                    # os.makedirs(dest, exist_ok=True)
                    #
                    # if ext == "png":
                    #     im = Image.open(path)
                    #     im.save( os.path.join(dest, f"{s}.jpg", format="JPEG", quality=90) )
                    # else: # txt and exr
                    #     shutil.copy(path, os.path.join ( dest, f"{s}.{ext}" ) )

                for root, folder, ext, desc in lbls: # no compression on the labels

                    path = os.path.join(root, folder, f"{s}.{ext}")

                    if not os.path.exists(path):
                        print(f"didn't find jpg {path}")

                    # dest = os.path.join(out_dir, lbl_folder, folder)
                    # os.makedirs(dest, exist_ok=True)
                    # shutil.copy(path, os.path.join ( dest, f"{s}.{ext}" ) )
            print(f"{count} done sofa")

            i += 1







    # sn_split = os.path.join("winsyn_riyal", ""
