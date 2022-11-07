import glob
import json
import os
import PIL
from pathlib import Path
from PIL import Image, ImageOps
import tags
import process_labels

dataset_root = Path.cwd()
orig     = os.path.join(dataset_root, "photos")
meta_dir = os.path.join(dataset_root, "metadata_single_elements")
web_dir  = os.path.join(dataset_root, "metadata_website")
use_cache = True

process_labels.USE_PRETTY_COLORS = True
process_labels.COLOR_MODE = process_labels.PRETTY

res = 128
quality = 50
name_map = {}

os.makedirs(web_dir, exist_ok=True)

all_tags = tags.all_tags.copy()
all_tags.append("no_meta")
all_tags.append("mesh")

# for batch in os.listdir(orig):
#     all_tags.append(batch)

for metadata_type in os.listdir(dataset_root):  # entry in an md folder gets you a tag
    if os.path.isdir(os.path.join(dataset_root, metadata_type)):
        all_tags.append(metadata_type)


def thumbnail(orig_path, thumb_path, rect=None, use_cache = False):

    if use_cache and os.path.exists(thumb_path):
        return

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

        for html_file, title, file_name in zip ([rects_html, index_html], ["<h3>crops (<a href='index.html'>photos</a>)</h3>", "<h3>(<a href='crops.html'>crops</a>) photos</h3>"], ["html_rects", "html_index"]):
            html_file.write("<html><body>\n")

            html_file.write(title)

            html_file.write("<style>\n")
            for tag_name in all_tags:
                html_file.write(f'input[type=checkbox].{tag_name}_c:checked ~ #batch>#content>.{tag_name}{{\n'
                           f'    display:inline;\n}}\n')
            for tag_name in all_tags:
                html_file.write(f'.{tag_name} \n{{\n    display:none\n}}\n')
            html_file.write("</style>\n")

            for idx, tag_name in enumerate ( os.listdir(orig) ): # batch names are also tagged here
                if os.path.isdir(os.path.join(orig, tag_name)):
                    html_file.write(f'<input class="{tag_name}_c" type="radio" value="{tag_name}_c" name="foo" onclick="set_batch(this.value);" {"checked" if idx == 0 else ""}>{tag_name}<a href="../photos/{tag_name}">[d]</a>\n')
                    if idx == 0:
                        first_batch = tag_name
            html_file.write(f'<br><hr>')
            for tag_name in tags.all_tags: # crop-tags we've defined
                html_file.write(f'<input class="{tag_name}_c" type="checkbox" value="{tag_name}_c" name="{tag_name}_foo">{tag_name} \n')
            html_file.write(f'<br><hr>')
            for tag_name in os.listdir(dataset_root): # available metadata also tags each file
                if os.path.isdir (os.path.join (dataset_root, tag_name)):
                    html_file.write(f'<input class="{tag_name}_c" type="checkbox" value="{tag_name}_c" name="{tag_name}_foo" {"checked" if tag_name == "photos" else ""}>{tag_name}\n')

            html_file.write(f'<br><hr>')


            # js to select a dataset for the professors
            html_file.write ("""<script>
                function getHashValue(key) {
                  var matches = location.hash.match(new RegExp(key+'=([^&]*)'));
                  return matches ? matches[1] : null;
                }
                
                // usage
                var hash = getHashValue('tab');
                const collection = document.getElementsByName("foo");
                
                for (let i = 0; i < collection.length; i++) {
                  if (collection[i].type == "radio" && collection[i].value== hash+"_c" ) {
                    collection[i].click();
                  }
                  if (hash == null && i == 0) collection[i].click();
                }
                
                async function fetchHtmlAsText(url) {
                    return await (await fetch(url)).text();
                }
                
                // this is your `load_home() function
                async function loadHome() {
                    const contentDiv = document.getElementById("content");
                    contentDiv.innerHTML = await fetchHtmlAsText("home.html");
                }
                
                async function set_batch(c) { 
                    batch_name = c.slice(0,-2)
                    const contentDiv = document.getElementById("batch"); 
                """)

            html_file.write(f"        contentDiv.innerHTML = await fetchHtmlAsText(batch_name+'/{file_name}.html')\n" # select the first batch after load
                            f"}}\n"
                            f"document.addEventListener('DOMContentLoaded', function() {{"
                            f"set_batch('{first_batch}_c')"
                            f"}}, false);\n")
            html_file.write ("""

</script>
<div id='batch'></div>
</body></html>""" )

        for batch in os.listdir(orig):

            if not os.path.isdir(os.path.join(orig, batch)):
                continue

            # ["tom_archive_19000101", "tom_bramley_20220406", "tom_saffron_20220418", "tom_cams_20220418", "tom_dales_20220403", "tom_leeds_docks_20220404", "tom_london_20220418", "tom_york_20220411"]:

            total_jpgs = 0
            index_append = ""
            rects_append = ""
            batch_thumbs = os.path.join(web_dir, batch)

            # per-batch cache file (assume nothing else has changed)
            append_index_file = os.path.join(batch_thumbs, "html_index.html")
            append_rect_file  = os.path.join(batch_thumbs, "html_rects.html")

            if use_cache and os.path.exists (append_index_file) and os.path.exists (append_rect_file):

                # cache files found, let's use those
                print(f"using cached version for {batch}")
                index_append = open(append_index_file, "r").read()
                rects_append = open(append_rect_file , "r").read()
            else:
                single_element_dir = Path(orig).parent.joinpath("metadata_single_elements/%s" % os.path.basename(batch))
                labels_dir = Path(orig).parent.joinpath("metadata_window_labels/%s" % os.path.basename(batch))

                photos_dir = os.path.join(orig, batch)

                os.makedirs(batch_thumbs, exist_ok=True)
                count = 0
                rect_count = 0

                index_append += (f"<div id='content'>") # wrap all in a div
                rects_append += (f"<div id='content'>")

                for photo in os.listdir(photos_dir):
                    if photo.endswith(".JPG") or photo.endswith(".jpg"):

                        print(f'{batch} {count} {photo}')
                        count += 1

                        pre, _ = os.path.splitext(photo)
                        json_file = pre + ".json"
                        json_file_path = os.path.join(meta_dir, batch, json_file)
                        labels_json_path = os.path.join(labels_dir, pre + ".json")
                        labels_png_path = os.path.join(labels_dir, pre + ".png")

                        # use image-with labels as thumbnail where available
                        if os.path.exists(labels_json_path): # render json to image if required
                            process_labels.render_labels_web(dataset_root, labels_json_path, flush_html=False, use_cache=False)
                            thumbnail( os.path.join(labels_dir, photo), os.path.join(batch_thumbs, photo), use_cache=False )
                        else:
                            thumbnail(os.path.join(photos_dir, photo), os.path.join(batch_thumbs, photo), use_cache=use_cache)

                        # read in the crop metadata
                        if os.path.exists (json_file_path):
                            metadata = json.load( open( json_file_path, "r" ) )
                        else:
                            metadata = {}
                            metadata["tags"] = ["no_meta"]
                            metadata["rects"] = []

                        tags = set(metadata["tags"]) # whole image tags
                        # tags.add(batch) - no! we shall all batches because we now use radio

                        for md in os.listdir(dataset_root): # all data-types that match batch/name-with-any-extension
                            for photo_data in glob.glob(os.path.join(dataset_root, md, batch) + "/" + pre + "*"):
                                tags.add(md)

                        photo_pre, ext = os.path.splitext(photo)
                        index_tags = tags.copy()

                        for thumb_idx, r in enumerate ( metadata["rects"] ):

                            print ("    crop %d" % thumb_idx)
                            crop_file = photo+"_crop_%d.jpg" % thumb_idx

                            rect_tags = tags.copy().union(set(r[1])) # per-photo-tags too
                            rect = r[0]

                            if rect[2] - rect[0] < 20 or rect [3] - rect[1] < 20:
                                print ("skipping small rect")
                                continue

                            thumbnail(os.path.join(photos_dir, photo),  os.path.join(batch_thumbs, crop_file), rect=r[0], use_cache=use_cache)

                            rects_append += (
                                f'<div class="{" ".join(rect_tags)}">'
                                f'<a href="{batch}/{photo_pre}.html">'
                                       f'<img src="{batch+"/"+crop_file}" alt="{batch}:{photo}:{thumb_idx}" width="64" height="64" loading="lazy" border="1"></a>\n'
                                f'</div>')

                            # photo page takes tags of all crops
                            index_tags = index_tags.union(set(r[1]))
                            rect_count += 1

                        photo_page_path = os.path.join(web_dir, batch, pre + ".html")
                        if not ( use_cache and os.path.exists(photo_page_path) ):
                            with open(photo_page_path, 'w') as photo_html:
                                photo_html.write("<html><body>\n")
                                photo_html.write(f"<h3>{batch} {photo}</h3><p>whole-image-tags: {' '.join(metadata['tags'])}</p>")
                                photo_html.write(f"<a href='../../photos/{batch}/{photo}'><img src='../../photos/{batch}/{photo}' height='640'></a><br><br>\n")

                                if os.path.exists ( os.path.join(labels_dir, photo_pre+".jpg") ):
                                    photo_html.write(f"<a href='../../metadata_window_labels/{batch}/{photo}'><img src='../../metadata_window_labels/{batch}/{photo_pre}.jpg' height='640'></a><br><br>\n")

                                if os.path.exists(labels_png_path):
                                    photo_html.write(f"<a href='../../metadata_window_labels/{batch}/{pre}.png'><img src='../../metadata_window_labels/{batch}/{pre}.png' height='640'></a><br><br>\n")

                                for thumb_idx, r in enumerate(metadata["rects"]):
                                    crop_file = photo+"_crop_%d.jpg" % thumb_idx
                                    if rect[2] - rect[0] < 20 or rect[3] - rect[1] < 20:
                                        print("skipping small rect")
                                        continue
                                    photo_html.write(f'crop {thumb_idx} with tags: {", ".join(r[1])}<br>')
                                    photo_html.write(f'<img src="{crop_file}" alt="{batch}:{photo}:{thumb_idx}" width="128" height="128" loading="lazy"><br><br>')

                                photo_html.write(f"<br><p>all metadata:</p><ul>")
                                for md in os.listdir(dataset_root):
                                    for photo_data in glob.glob(os.path.join(dataset_root, md, batch)+"/"+pre+"*"):
                                        md_path, md_ext = os.path.splitext(photo_data)
                                        md_path_strs = os.path.split(photo_data)

                                        if os.path.isdir(photo_data):
                                            if (os.path.exists(os.path.join(photo_data, "clean", "mesh.zip"))):
                                                photo_html.write(f'<li><a href="../OBJViewer.html?fileURL=../{md}/{batch}/{md_path_strs[1]}/clean/mesh.zip"> {md} mesh</a></li>')
                                                photo_html.write(f'<li><a href="../../{md}/{batch}/{md_path_strs[1]}">{md} mesh photo dir</a></li>')
                                        else:
                                            photo_html.write(f'<li><a href="../../{md}/{batch}/{md_path_strs[1]}">{md} {md_ext.lower()}</a></li>')

                                photo_html.write(f'</ul>')

                                photo_html.write("</body></html>\n")

                        index_append += (
                            f'<div class="{" ".join(index_tags)}">'
                            f'<a href="{batch}/{photo_pre}.html">'
                                   f'<img src="{batch+"/"+photo}" alt="{batch+"/"+photo}" width="64" height="64" loading="lazy" border="1"></a>\n'
                            f'</div>')

                index_append += (f"<p>image count:{count}</p>")
                index_append += (f"</div>")
                rects_append += (f"<p>crop count:{rect_count}</p>")
                rects_append += (f"</div>")

                open(append_index_file, "w").write(index_append)
                open(append_rect_file, "w").write(rects_append)

            # index_html.write (index_append)
            # index_html.flush()
            # rects_html.write (rects_append)
            # rects_html.flush()

        index_html.write("</body></html>\n")
        rects_html.write("</body></html>\n")
