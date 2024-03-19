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

def many_syn(rgbs, dataset_root, output_folder):
    '''
    Render out labelled dataset
    '''

    random.shuffle(rgbs)
    img_dir = os.path.join(output_folder, "imgs")
    os.makedirs(img_dir, exist_ok=True)


    grid_image = Image.new('RGB', (512, 512))

    with open(os.path.join(output_folder,"index.html"), 'w') as index_html:

        index_html.write("""
        <html>
          <head><script>
    	      function setPane(name) {
		  demo_showing = name;
	    document.getElementById("demo_desc").innerHTML = "synthetic<br/>name: "+demo_showing;
		  setRGB();
	      }
	      function setLabel() {
            document.getElementById("demo_pane").src = "imgs/"+demo_showing+".png";
	      }
	      function setRGB() {
            document.getElementById("demo_pane").src = "imgs/"+demo_showing+".jpg";
	      }
	      function showHoverRGB(name){
            document.getElementById("demo_pane").src = "imgs/"+name+".jpg";
	      }
	      function hideHoverRGB() {
		  setRGB();
	      }
    window.onload = function(e){
    """
                         )
        zn = Path(rgbs[0]).with_suffix("").name
        index_html.write(f"setPane('{zn}');")
        index_html.write("""
 }
    </script><style>
    #demo_container :hover {
        border: 10px;
        background: #000000;
        background: var(--label);
    }
    </style>
    </head><body>
        """
                         )

        index_html.write('<div style="position: relative; width:50%; max-width:512px; display:inline-block;">')
        index_html.write('<img src="index.jpg" style="width: 100%; height: auto;">')

        for i, rgb_file in enumerate ( rgbs ):

            fn = Path(rgb_file).with_suffix("").name
            xpos = i % 16
            ypos = i // 16
            if ypos >= 16:
                break

            rgb_img = Image.open(rgb_file)
            rgb_img = rgb_img.convert('RGB')
            lil = rgb_img.resize([32,32])
            grid_image.paste(lil, [xpos*32, ypos*32] )
            label_file = Path(rgb_file).parent.parent.joinpath("labels").joinpath(Path(rgb_file).name )

            rgb_img.save(os.path.join(img_dir, f"{fn}.jpg"), quality=95 )
            shutil.copyfile(label_file, os.path.join(img_dir, f"{fn}.png") )

            index_html.write(f'<div style="position:absolute; left:{xpos*100/16.}%; top:{ypos*100/16.}%; width:{1.*100/16}%; height:{1.*100/16}%;" onclick="setPane(\'{fn}\');" onmouseenter="showHoverRGB(\'{fn}\');" onmouseleave="hideHoverRGB()"></div>\n');

            print(f" {xpos} -- {ypos} ")

        index_html.write(f'</div>\n')
        index_html.write(f'<div id="demo_container" style="width:50%; max-width:512px; display:inline-block; position: relative;">\n')
        index_html.write(f'<div style="opacity: 0.7; background:#000; color:#FFF; padding: 0px 6px 0px 6px; position: absolute; bottom: 5px; left:5px; border-color:#000000;border-radius:5px;-moz-border-radius:5px;-webkit-border-radius:5px;"><p id="demo_desc" style="margin-block-start: 2px; margin-block-end: 2px;">click on images on the left for more information</p></div>\n')
        index_html.write(f'<img src="imgs/{Path(rgbs[0]).with_suffix("").name}.jpg" id="demo_pane" style="width:100%;" onmouseenter="setLabel();" onmouseleave="setRGB()">\n')
        index_html.write(f'</div>\n')
        index_html.write('</body>\n')
        index_html.write('</html>\n')

    grid_image.save ( os.path.join(output_folder, "index.jpg") )

if __name__ == "__main__":

    if platform == "win32":
        dataset_root = r"C:\Users\twak\Downloads\snow_200"
        output_folder = r"C:\Users\twak\Downloads\ad_syn"
    else:
        dataset_root = r"/media/twak/Saudi Data Raid/work_22_24/winsyn_riyal/winsyn_riyal"
        output_folder = r"/home/twak/Downloads/winsyn_demo/"

    os.makedirs(output_folder, exist_ok=True)

    rgbs = []
    rgbs.extend (glob.glob(os.path.join(dataset_root, "rgb", "*.png")))

    many_syn(rgbs, dataset_root, output_folder)

