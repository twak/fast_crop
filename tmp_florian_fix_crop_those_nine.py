import json
import os
from PIL import Image, ImageOps, ExifTags
import defusedxml
from pathlib import Path

# the files in the below folder were hard-cropped before being soft-cropped and sent to the labellers. This script
# pulls the (lightroom?!) metadata about the crop to convert the labels to the new coordinate system.
cropped_path = r"C:\Users\twak\Documents\architecture_net\dataset\photos\Michaela_Windows_Vienna_20220505"
orig_file_dirs= [r"C:\Users\twak\Documents\architecture_net\dataset\photos\michaela_vienna_20220427", r"C:\Users\twak\Documents\architecture_net\dataset\photos\michaela_vienna_20220428"]

for f in os.listdir(cropped_path):

    if  "XXX" in f:
        continue

    print (f)
    im = Image.open(os.path.join (cropped_path, f))

    top    = float (im.getxmp()['xmpmeta']['RDF']['Description']['CropTop'] )
    bottom = float (im.getxmp()['xmpmeta']['RDF']['Description']['CropBottom'] )
    left   = float (im.getxmp()['xmpmeta']['RDF']['Description']['CropLeft'] )
    right  = float (im.getxmp()['xmpmeta']['RDF']['Description']['CropRight'] )

    orig_file = None
    for o in orig_file_dirs:
        op = os.path.join(o, f)
        if os.path.exists (op):
            orig_file = op

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation]=='Orientation':
            break

    oim = Image.open (orig_file)
    exif=dict(oim._getexif().items())

    if exif[orientation] == 3: # 180
        print("180 ccw")
        top, bottom = 1.-bottom, 1.-top
        left, right = 1-right, 1-left
    elif exif[orientation] == 6: # 270 ccw # good.
        top, right, bottom, left = left, 1 - top, right, 1 - bottom
        print("270 ccw")
    elif exif[orientation] == 8: # 90 ccw
        bottom, left, top, right = 1-left, top, 1-right, bottom
        print("90 ccw")
    else:
        print("0 ccw")

    # oim = Image.open (orig_file)
    # oim = ImageOps.exif_transpose(oim)

    # if not "8507" in f: #?!
    #     oim_c = oim.crop((int(left * oim.width), int(top * oim.height), int(right * oim.width), int(bottom * oim.height)))
    #     oim_c = ImageOps.exif_transpose(oim_c)
    # else:
    #     oim_c = oim
    #     oim_c = oim_c.transpose(Image.ROTATE_270)
    #     oim_c= oim_c.crop((int((1.-bottom) * oim_c.width), int(left * oim_c.height), int((1.-top) * oim_c.width), int(right * oim_c.height)))

    # oim_c.save(os.path.join (cropped_path, f+"XXX.jpg"), "JPEG")

    # plan: 1/ load label json, 2/ update json with above crop locations, 3/ write to a new folder -render and check!
    #_NZ7-008130.jpg 7c6fba3ef08c

    batch = Path(orig_file).parent.name
    basename = os.path.splitext(f)[0]
    json_file = Path(orig_file).parent.parent.parent.joinpath("metadata_window_labels").joinpath(batch).joinpath(basename + ".json")
    json_file_fixed = Path(orig_file).parent.parent.parent.joinpath("metadata_window_labels").joinpath(batch+"_new").joinpath(basename + ".json")
    os.makedirs(Path(json_file_fixed).parent, exist_ok=True)

    with open(json_file, "r") as f2:
        attribs = json.load(f2)
        print (attribs)

        old_crop = attribs[list(attribs.keys())[0]]["crop"]

        name = list(attribs.keys())[0]
        attribs[name]["crop"] = [int(left * oim.width)+old_crop[0], int(top * oim.height)+old_crop[1],
                                 int(left * oim.width) + old_crop[2],
                                 int(top * oim.height) + old_crop[3] ]

                                 # int(right * oim.width) - (old_crop[2] + int(left * oim.width)),
                                 # int(bottom * oim.height) - (old_crop[3] + int(top * oim.height) )]
        attribs["_new"+name] = attribs.pop (name)

        with open(json_file_fixed, "w") as f3:
            json.dump(attribs, f3)


    print(im.getxmp())
    print (f"{top} {bottom} {left} {right}")
    print (orig_file)
    im.width

    print()

