import glob
import json
import os
from PIL import Image, ImageOps
from pathlib import Path

# this is a script to update from "single set of tags per photo" to "tags per rectangle"

def json_file(self, pth=None):
    if pth == None:
        pth = self.input_loc

    pre, ext = os.path.splitext(pth)

    return os.path.join(self.meta_dir, os.path.basename(pre) + ".json")

def old_to_new(old_folder, new_folder):

    images=[]
    images.extend(glob.glob(old_folder + "/**.JPG"))
    # images.extend(glob.glob(old_folder + "/**.jpg"))

    for i in images:

        print (i)

        pre, _ = os.path.splitext(i)
        json_file = pre + ".json"

        if os.path.exists(json_file):
            old = json.load(open(json_file, "r"))
            old_rects = old["rects"]
            if "tags" in old:
                old_tags = old["tags"]
            else:
                old_tags = []
        else:
            old = {} # code below adds in a window rectangle for this dimension
            im = Image.open(i)
            im = ImageOps.exif_transpose(im)
            old["width" ] = im.width
            old["height"] = im.height
            old_rects=[]
            old_tags=[]

        rects = []

        if len ( old_rects ) == 0:
            old_rects.append([0,0,old["width"], old["height"]])

        for r in old_rects:
            r_tags = []

            if "street" in old_tags:
                old_tags.append("shop")

            r_tags = set(old_tags).intersection(set(["glass_facade", "church", "shop", "abnormal", "window"]))

            r_tags.add("window")
            rects.append([r,list(r_tags)])

        tags=[] # whole image tags
        if "deleted" in old_tags:
            tags.append("deleted")

        out = {"rects": rects, "width": old["width"], "height": old["height"], "tags": tags}

        file_name = os.path.basename(pre) +".json"

        with open(os.path.join(new_folder, file_name), "w") as file:
            json.dump(out, file)

if __name__ == "__main__":

    orig = "C:\\Users\\twak\\Documents\\architecture_net\\dataset\\photos"
    for f in os.listdir(orig):

        if f.startswith("tom_archive") or f.startswith("Michaela_Windows"):
            continue

        meta_dir = Path(orig).parent.joinpath("metadata_single_elements/%s" % os.path.basename(f) )

        os.makedirs(meta_dir, exist_ok=True)
        old_to_new( os.path.join (orig, f), meta_dir)