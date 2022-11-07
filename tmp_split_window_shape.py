import glob
import os.path
import re

'''
create a split.txt file based on the window shape in the attributes file.
'''


iter = -1

logs = glob.glob("./attribs/*.txt")
from pathlib import Path
experiments = {}

count_rect = 0
count_other = 0

with open("./split_rects.txt", "w") as split_rects:
    with open("./split_non_rects.txt", "w") as split_other:
        for log in logs:
            print (log)

            root_name = os.path.splitext( Path(log).name )[0]

            n = int ( root_name )
            experiments[n] = experiment = {}
            with open(log) as fp:
                shape = -1
                shape_rect_extra_h = -1
                for line in fp:
                    res = re.search("([^:]*):(.*)", line)
                    if res:
                        # print (f" {res.group(1)}   {res.group(2)} ")
                        key = res.group(1)
                        value = res.group(2)
                        if key == "shape_border_gen":
                            shape = int(value)
                        if key == "shape_rect_extra_h":
                            shape_rect_extra_h = float(value)

                if shape <= 3 and shape_rect_extra_h < 0.1: # is a rectangle!
                    count_rect += 1
                    split_rects.write(root_name+"\n")
                else: # other shape
                    count_other += 1
                    split_other.write(root_name+"\n")

print (f"found {count_rect} rectangular windows and {count_other} with other shapes ")
