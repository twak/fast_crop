import os
import glob
import argparse
import json

from xml.etree import ElementTree as ET

import pandas as pd

KEYS = ['Source', 'Date', 'Time', 'Latitude', 'Longitude', 'Country', 'City']

def get_json_data(json_file):
    json_file = open(json_file)
    json_data = json.load(json_file)
    #print(json_data)
        
    for key, value in json_data.items():        
        if key == KEYS[3]:
            lat = value
        if key == KEYS[4]:
            lon = value

    return lat, lon

def get_html_data(folder_name, image_name):
    html_file = image_name + ".html"
    html_file = os.path.join("..", folder_name, html_file)
    #html_file = html_file.replace("\\","/")
    anchor_data = "<a href ='"
    anchor_data = anchor_data + html_file + "'>"

    image_file = image_name + ".JPG"
    image_file = os.path.join("..", folder_name, image_file)
    #image_file = image_file.replace("\\","/")
    image_src = "<img src ='"
    image_src = image_src + image_file + "'>"

    br_tag = "<br/>" + image_name + "<\\a>"

    html_data = anchor_data + image_src + br_tag

    return html_data


'''
<a href='../artur_saopaulo_20230208/DSC00275.html'>
        <img src='../artur_saopaulo_20230208/DSC00276.JPG'><br/>DSC00275<\a>
'''

def process_json_files(folder, js_data):
    # Get the json files in the folder
    json_files = sorted(glob.glob(folder + "/**.json"))
    no_files = len(json_files)
    print("No. of Json Files, {0} in folder, {1}."
        .format(no_files, folder))
    folders = folder.split(os.sep)
    folder_name = folders[-1]
    print(folder_name)
    index = 0
    for json_file in json_files:        
        lat, lon = get_json_data(json_file)
        base_name = os.path.basename(json_file)        
        base_name = os.path.splitext(base_name)[0]
        #html_file = base_name + ".html" 
        #image_file = base_name + ".JPG"               
        #print(base_name, html_file, image_file, lat, lon)
        html_data = get_html_data(folder_name, base_name)
        #print(html_data)
        data = [lat, lon, html_data]
        js_data.append(data)
        index = index + 1

        print("Processed {0} out of {1} images.". 
                format(index, no_files), end='\r')
    return js_data

def write_js_data(js_data, out_file):
    out_data =  open(out_file, 'w')
    out_data.write("var addressPoints = [")
    for data in js_data:
        #print(data)
        out_data.write("[")            
        out_data.write('%f' % data[0])
        out_data.write(",")
        out_data.write('%f' % data[1])
        out_data.write(",\"")
        out_data.write('%s' % data[2])
        out_data.write("\"],\n")
        
    out_data.write("];")
    out_data.close()

    print("Written data to file, ", out_file)

    
if __name__ == "__main__":    

    parser = argparse.ArgumentParser(
                description="Generate Location Lat, Lons, links \
                        from JSON files.")

    # Parse Images data path
    parser.add_argument("--path", type=str,
                        help="JSONs locations path.")

    # Parse Images data path
    parser.add_argument("--out_file", type=str,
                        help="Output in JS file.")
    
    args = parser.parse_args()
    # Parse command line value to in path
    path = args.path

    out_file = args.out_file

    is_process = True

    if not os.path.exists(path):
        print("Locations path, {0} does not exists.".format(path))
        is_process = False

    if is_process:
        print("Process Futher.")

        # Get directories from the given path
        folders = [f.path for f in os.scandir(path) if f.is_dir()]
        folders = sorted(folders)
        js_data = []
        index = 0
        for folder in folders:  
            print("Generating java script data for ", folder)          
            js_data = process_json_files(folder, js_data)  
            print("Processed java script data for ", folder)
            

        write_js_data(js_data, out_file)
                            
        
    print("Generating Lat Lon Tool done.")


    '''
    [-22.581568,-46.522850,"<a href='../artur_saopaulo_20230208/DSC00275.html'>
        <img src='../artur_saopaulo_20230208/DSC00276.JPG'><br/>DSC00275<\a>"]
    '''
