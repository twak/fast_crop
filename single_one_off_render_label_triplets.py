import process_labels
import os, json, PIL, glob
from process_labels import find_photo_for_json, label_color_mode, crop
from PIL import Image, ImageDraw, ImageOps
import svgwrite
from sys import platform
from pathlib import Path
import process_labels

def render_labels_per_crop( dataset_root, json_file, output_folder, res=512, mode='None'):
    '''
    This is mostly for checking the labels from the labellers...
    '''

    colors = process_labels.colours_for_mode(process_labels.PRETTY)

    print (f"rendering crops from {json_file} @ {res}:{mode}")

    pj = Path(json_file)
    photo_file = pj.with_suffix(".jpg").name

    os.makedirs(os.path.join(output_folder, "rgb"   ), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "twofer"), exist_ok=True)

    with open(json_file, "r") as f:
        data = json.load(f)

    photo = Image.open( os.path.join(dataset_root, "crops", photo_file) )
    label_mode = "RGBA"

    # crop to each defined region
    for crop_name, crop_data in data.items():

        # if os.path.exists(os.path.join(output_folder, "twofer", crop_name + ".jpg")):
        #     continue

        #crop_bounds = crop_data["crop"]
        crop_photo =photo #.crop (crop_bounds)

        label_img = Image.new(label_mode, (crop_photo.width, crop_photo.height))
        draw_label_photo = ImageDraw.Draw(label_img, label_mode)
        draw_label_photo.rectangle([(0, 0), (label_img.width, label_img.height)], fill=colors["none"] )

        draw_label_trans_img = crop_photo.copy()
        draw_label_trans = ImageDraw.Draw(draw_label_trans_img, 'RGBA')

        dwg = svgwrite.Drawing(os.path.join(output_folder, "twofer", crop_name + ".svg"), profile='tiny')
        dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
        dwg.add(dwg.text(crop_name, insert=(0, 0.2), fill='black'))


        for catl in crop_data["labels"]:

            cat=catl[0]

            for poly in catl[1]:
                poly = [tuple(x) for x in poly]
                draw_label_photo.polygon( poly, colors[cat])
                draw_label_trans.polygon( poly, (* ( colors[cat]), 180), outline = (0,0,0), width=6 )

                dwg.add ( dwg.polygon(poly, fill=f'rgb({colors[cat][0]},{colors[cat][1]},{colors[cat][2]})') )

                # p = Path(fill=f'rgb({colors[cat][0]},{colors[cat][1]},{colors[cat][2]})')
                # p.push(f'm {poly[0][0]} {poly[0][1]}')
                # for x in poly:
                #     p.push(f'l {x[0], x[1]}')
                # dwg.add(p)

        dwg.save()

        # output at native res
        crop_name = os.path.splitext(crop_name)[0]
        # crop_photo.save(os.path.join(output_folder, "rgb"   , crop_name + ".jpg"))
        # label_img .save(os.path.join(output_folder, "labels", crop_name + ".png"))

        # crop down
        crop_photo           = crop(crop_photo, res, mode, resample=Image.Resampling.LANCZOS, background_col="black")
        label_img            = crop(label_img , res, mode, resample=Image.Resampling.NEAREST, background_col="white")
        draw_label_trans_img = crop(draw_label_trans_img , res, mode, resample=Image.Resampling.NEAREST, background_col="black")

        # cat all three images
        triplet = Image.new('RGB', (crop_photo.width + label_img.width + draw_label_trans_img.width, crop_photo.height))
        triplet.paste(crop_photo, (0, 0))
        triplet.paste(label_img, (crop_photo.width, 0))
        triplet.paste(draw_label_trans_img, (crop_photo.width + label_img.width, 0))
        triplet .save(os.path.join(output_folder, "twofer", crop_name + ".jpg"))

if __name__ == "__main__":


    if platform == "win32":
        dataset_root = r"C:\Users\twak\Documents\architecture_net\windows_part3"
    else:
        dataset_root = r"/mnt/vision/data/archinet/data"

    s = "_lyd_24_2"

    output_folder = r"C:\Users\twak\Documents\architecture_net\windows_part3\triplets"+s

    json_src = []
    #json_src.extend(glob.glob(r'/home/twak/Downloads/LYD__KAUST_batch_2_24.06.2022/LYD<>KAUST_batch_2_24.06.2022/**.json'))
    json_src.extend(glob.glob(os.path.join(r"C:\Users\twak\Documents\architecture_net\windows_part3\labels"+s, "*.json")))

    # json_src.extend(glob.glob(os.path.join(dataset_root, "metadata_window_labels", "tom_archive_19000102", "*.json")))
    # json_src.extend(glob.glob(r'C:\Users\twak\Documents\architecture_net\dataset\metadata_window_labels\from_labellers\LYD__KAUST_batch_1_fixed_24.06.2022\**.json'))
    # render labels over whole photos for the website

    # for j in json_src:
    #     render_labels_web( dataset_root, j)
    # render labels, svg, transparencies for labeller QA

    # photos = []
    # photos.extend(glob.glob(os.path.join(dataset_root, "photos", "*", "*.JPG")))
    # photos.extend(glob.glob(os.path.join(dataset_root, "photos", "*", "*.jpg")))

    # count_photos(photos)

    for f in json_src:
        render_labels_per_crop( dataset_root, f, output_folder, res=1024, mode='none')
