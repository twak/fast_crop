import glob
import json
import os

import PIL

from pathlib import Path
from PIL import Image, ImageOps
import tags

orig = "C:\\Users\\twak\\Downloads\\update_test\\photos"
meta_dir = "C:\\Users\\twak\\Downloads\\update_test\\metadata_single_elements"
web_dir = "C:\\Users\\twak\\Downloads\\update_test\\metadata_website"

# orig = "C:\\Users\\twak\\Documents\\architecture_net\\dataset\\photos"
# meta_dir = "C:\\Users\\twak\\Documents\\architecture_net\\dataset\\metadata_single_elements"
# web_dir = "C:\\Users\\twak\\Documents\\architecture_net\\dataset\\metadata_website"

dataset_root = Path(orig).parent
res = 128
quality = 50
name_map = {}

os.makedirs(web_dir, exist_ok=True)

all_tags = tags.all_tags.copy()
for batch in os.listdir(orig):
    all_tags.append(batch)

def thumbnail(orig_path, thumb_path, rect=None):
    im = Image.open(orig_path)
    if len(im.getbands()) > 3:  # pngs..
        im = im.convert("RGB")
    im = ImageOps.exif_transpose(im)

    if rect is not None:
        im = im.crop((rect[0], rect[1], rect[2], rect[3]))

    width = im.size[1]
    height = im.size[0]
    wh = min(width, height)
    im = ImageOps.pad(im, (wh, wh), color="gray")
    im = im.resize((res, res), resample=PIL.Image.Resampling.BOX)
    im.save(thumb_path, format="JPEG", quality=quality)

with open(os.path.join(web_dir,"crops.html"), 'w') as rects_html:
    with open(os.path.join(web_dir,"index.html"), 'w') as index_html:

        for html_file, title in zip ([rects_html, index_html], ["<h3>crops (<a href='index.html'>photos</a>)</h3>", "<h3>(<a href='crops.html'>crops</a>) photos</h3>"]):
            html_file.write("<html><body>\n")

            html_file.write(title)

            html_file.write("<style>\n")
            for tag_name in all_tags:
                html_file.write(f'input[type=checkbox].{tag_name}_c:checked ~ .{tag_name}{{\n'
                           f'    display:inline;\n}}\n')
            for tag_name in all_tags:
                html_file.write(f'.{tag_name} \n{{\n    display:none\n}}\n')
            html_file.write("</style>\n")
            for tag_name in tags.all_tags:
                html_file.write(f'<input class="{tag_name}_c" type="checkbox" value="{tag_name}_c" name="{tag_name}_foo">{tag_name}   \n')

            for tag_name in os.listdir(orig):
                html_file.write(f'<input class="{tag_name}_c" type="checkbox" value="{tag_name}_c" name="{tag_name}_foo" checked>{tag_name}<br>\n')


        for batch in os.listdir(orig):

            single_element_dir = Path(orig).parent.joinpath("metadata_single_elements/%s" % os.path.basename(batch))

            photos_dir = os.path.join(orig, batch)
            # name_map = name_map.union ( ROI(photos_dir).cut_n_shut(web_dir, clear_log=True, crop_mode="square_expand", resolution=res, quality=quality) )

            batch_thumbs = os.path.join (web_dir, batch)
            os.makedirs(batch_thumbs, exist_ok=True)
            count = 0

            for photo in os.listdir(photos_dir):

                print(f'{batch} {count} ')
                count += 1

                if photo.endswith(".JPG") or photo.endswith(".jpg"):
                    thumbnail(os.path.join(photos_dir, photo), os.path.join(batch_thumbs, photo))

                    pre, _ = os.path.splitext(photo)
                    json_file = pre + ".json"

                    metadata = json.load( open( os.path.join(meta_dir, batch, json_file), "r" ) )

                    tags = set(metadata["tags"])
                    tags.add(batch)
                    for r in metadata["rects"]:
                        for t in r[1]:
                            tags.add(t)

                    photo_pre, ext = os.path.splitext(photo)

                    index_html.write(
                        f'<div class="{" ".join(tags)}">'
                        f'<a href="{batch}/{photo_pre}.html">'
                               f'<img src="{batch+"/"+photo}" alt="{batch+"/"+photo}" width="64" height="64" loading="lazy"></a>\n'
                        f'</div>')

                    with open(os.path.join(web_dir, batch, pre + ".html"), 'w') as photo_html:

                        photo_html.write("<html><body>\n")
                        photo_html.write(f"<h3>{batch} {photo}</h3><p>whole-image-tags: {' '.join(metadata['tags'])}</p>")
                        photo_html.write(f"<a href='../../photos/{batch}/{photo}'><img src='../../photos/{batch}/{photo}' height='640'></a><br><br>\n")

                        for thumb_idx, r in enumerate ( metadata["rects"] ):
                            crop_file=photo+"_crop_%d.jpg" % thumb_idx
                            thumbnail(os.path.join(photos_dir, photo),  os.path.join(batch_thumbs, crop_file), rect=r[0])

                            rects_html.write(
                                f'<div class="{" ".join(tags)}">'
                                f'<a href="{batch}/{photo_pre}.html">'
                                       f'<img src="{batch+"/"+crop_file}" alt="{batch}:{photo}:{thumb_idx}" width="64" height="64" loading="lazy"></a>\n'
                                f'</div>')

                            photo_html.write(f'crop {thumb_idx} with tags: {", ".join(r[1])}<br>')
                            photo_html.write(f'<img src="{crop_file}" alt="{batch}:{photo}:{thumb_idx}" width="128" height="128" loading="lazy"><br><br>')

                        photo_html.write(f"<br><p>all metadata:</p><ul>")
                        for md in os.listdir(dataset_root):
                            for photo_data in glob.glob(os.path.join(dataset_root, md, batch)+"/"+pre+".*"):
                                _, md_ext = os.path.splitext(photo_data)
                                photo_html.write(f'<li><a href="{photo_data}">{md} {md_ext.lower()}</a></li>')
                        photo_html.write(f'</ul>')


                        photo_html.write("</body></html>\n")

        index_html.write("</body></html>\n")
        rects_html.write("</body></html>\n")
