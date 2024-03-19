import copy
import glob
import hashlib
import json

# from the index file when we created the crops for the labellers to our src coordinate system
import os
import random
import shutil
import time
from collections import defaultdict
from os import path
from pathlib import Path
import PIL
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import svgwrite
from PIL import ImageOps
import numpy as np
from sys import platform
import hashlib
from PIL.Image import Transpose
import process_labels

def to_color_labels(png_file):

    print(png_file)

    grey = Image.open(png_file, "r")
    label = np.asarray(grey)#[:, :, 0:3]
    color_seg = np.zeros((grey.size[0], grey.size[1], 3), dtype=np.uint8)

    for i, l_name in enumerate ( process_labels.LABEL_SEQ_NO_DOOR ):
        color = process_labels.colours_for_mode(process_labels.PRETTY)[l_name]
        color_seg[i == label, :] = color

    return Image.fromarray( color_seg )

def many_syn(synths, reals, output_folder):

    random.shuffle(synths)
    random.shuffle(reals)

    img_dir = os.path.join(output_folder, "imgs")
    os.makedirs(img_dir, exist_ok=True)

    grid_image = Image.new('RGB', (512, 512))

    samples = []


    for i in range(128):
        name = Path(reals[i]).with_suffix("").name
        samples.append( (reals[i],  Path(reals[i]).parent.parent.joinpath("labels").joinpath(name+".png"), "real<br/>name: "+name) )

    for i in range(128):
        name = Path(synths[i]).with_suffix("").name
        samples.append( (synths[i],  Path(synths[i]).parent.parent.joinpath("labels_8bit").joinpath(name+".png"), "synthetic<br/>name: "+name) )

    rest = samples[1:]
    random.shuffle(rest)
    shuffled_lst = [samples[0]] + rest
    samples = shuffled_lst

    with open(os.path.join(output_folder,"index.html"), 'w') as index_html:

        index_html.write("""
        <html>
          <head><script>
    	    function setPane(name, desc) {
		    demo_showing = name;
		    setRGB(desc);
	      }
	      function setLabel() {
            document.getElementById("demo_pane").src = "imgs/"+demo_showing+".png";
	      }
	      function setLabel2(name) {
            document.getElementById("demo_pane").src = "imgs/"+name+".png";
	      }
	      function setRGB(desc) {
	        desc_showing = desc;
            document.getElementById("demo_pane").src = "imgs/"+demo_showing+".jpg";
            document.getElementById("demo_desc").innerHTML = desc_showing
	      }
	      function showHoverRGB(name, desc){
            document.getElementById("demo_pane").src = "imgs/"+name+".jpg";
            document.getElementById("demo_desc").innerHTML = desc
	      }
	      function hideHoverRGB() {
		    setRGB(desc_showing);
	      }
    window.onload = function(e){
    """
                         )
        zn = Path(samples[0][0]).with_suffix("").name
        index_html.write(f"setPane('{zn}','{samples[0][2]}');")
        index_html.write("""
 }
    </script>
    </head><body>
        """
                         )

        index_html.write('<div style="position: relative; width:49%; max-width:512px; display:inline-block;">')
        index_html.write('<img src="index.jpg" style="width: 100%; height: auto;">')

        i = 0
        for rgb_file, label_file, html_desc in samples:
            # rgb_file, label_file, html_desc = data

            fn = Path(rgb_file).with_suffix("").name
            # label_file = Path(rgb_file).parent.parent.joinpath("labels").joinpath(Path(rgb_file).name)

            if not (os.path.exists(rgb_file) and os.path.exists(label_file)):
                continue

            xpos = i % 16
            ypos = i // 16
            if ypos >= 16:
                break

            rgb_img = Image.open(rgb_file)
            rgb_img = rgb_img.convert('RGB')
            lil = rgb_img.resize([32,32])
            grid_image.paste(lil, [xpos*32, ypos*32] )


            rgb_img.save(os.path.join(img_dir, f"{fn}.jpg"), quality=95 )

            to_color_labels(label_file).save( os.path.join(img_dir, f"{fn}.png") )

            index_html.write(f'<div style="position:absolute; left:{xpos*100/16.}%; top:{ypos*100/16.}%; width:{1.*100/16}%; height:{1.*100/16}%;" onclick="setPane(\'{fn}\', \'{html_desc}\');" onmouseenter="showHoverRGB(\'{fn}\', \'{html_desc}\');" onmouseleave="hideHoverRGB()" onmousedown="setLabel2(\'{fn}\');"></div>\n');

            print(f" {xpos} -- {ypos} ")
            i+=1

        index_html.write(f'</div>\n')
        index_html.write(f'<div id="demo_container" style="width:49%; max-width:512px; display:inline-block; position: relative;">\n')
        index_html.write(f'<div style="opacity: 0.7; background:#000; color:#FFF; padding: 0px 6px 0px 6px; position: absolute; bottom: 5px; left:5px; border-color:#000000;border-radius:5px;-moz-border-radius:5px;-webkit-border-radius:5px;"><p id="demo_desc" style="margin-block-start: 2px; margin-block-end: 2px;">click on images on the left for more information</p></div>\n')
        index_html.write(f'<img src="imgs/{Path(synths[0]).with_suffix("").name}.jpg" id="demo_pane" style="width:100%; aspect-ratio : 1 / 1;" onmouseenter="setLabel();" onmouseleave="hideHoverRGB()">\n')
        index_html.write(f'</div>\n')
        index_html.write('</body>\n')
        index_html.write('</html>\n')

    grid_image.save ( os.path.join(output_folder, "index.jpg"), quality=98 )

if __name__ == "__main__":

    output_folder = "/home/twak/Downloads/winsyn_demo"
    os.makedirs(output_folder, exist_ok=True)

    synths = []
    synths.extend (glob.glob(os.path.join(r"/media/twak/Saudi Data Raid/work_22_24/winsyn_riyal/winsyn_riyal", "rgb", "*.png")))

    reals = []
    reals.extend (glob.glob(os.path.join(r"/media/twak/Saudi Data Raid/work_22_24/winlab_5/", "rgb", "*.jpg")))

    many_syn(synths, reals, output_folder)

