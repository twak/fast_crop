import os
import glob
import argparse
import json

import csv



HEADER = ["source", "No. of files", "No. source:Camera", 
             "No. source:Track","No. source:Coarse",]
SOURCES = ['camera', 'track', 'coarse']


def get_json_source(json_file:str) -> str:

    """Gets source in the json file

    Args:
      json_file: json file including path      

    Returns:
     str: source of the data
    
    """

    json_file = open(json_file)
    json_data = json.load(json_file)
           
    for key, value in json_data.items():        
        if key == 'Source':
            source = value
            break        
    return source
    


def get_stats(path:str) -> list[int]:
    """Gets statistics in a given path

    Args:
      path: path in the system      

    Returns:
      List of ints: no_files, source_camera, source_track, source_coarses 
    
    """

    no_cameras = 0
    no_tracks = 0
    no_coarses = 0
    json_files = sorted(glob.glob(folder + "/**.json"))
    
    for json_file in json_files: 
        source = get_json_source(json_file)            
        
        if source == SOURCES[0]:
            no_cameras = no_cameras  + 1            

        if source == SOURCES[1]:
            no_tracks = no_tracks  + 1            

        if source == SOURCES[2]:
            no_coarses = no_coarses  + 1  

    sources = [len(json_files), no_cameras, no_tracks, no_coarses]

    return sources

def get_source_counts(data:list) -> list[int]:
    counts = ["", 0, 0, 0, 0]
    for row_data in data:
        counts[1] = counts[1] + row_data[1]
        counts[2] = counts[2] + row_data[2]
        counts[3] = counts[3] + row_data[3]
        counts[4] = counts[4] + row_data[4]

    return counts

def write_csv_file(out_file:str, data:list) -> None:
    with open(out_file, 'w') as file:
        writer = csv.writer(file)
        counts = get_source_counts(data)
        writer.writerow(counts)
        writer.writerow(HEADER)

        for row_data in data:
            writer.writerow(row_data)

    return
    
if __name__ == "__main__":    

    parser = argparse.ArgumentParser(
                description="Generate Location Lat, Lons, links \
                        from JSON files.")

    # Parse Images data path
    parser.add_argument("--path", type=str,
                        help="Locations path.")

    # Parse Images data path
    parser.add_argument("--out_file", type=str,
                        help="Output CSV File.")
    
    args = parser.parse_args()

    # Parse command line value to path
    path = args.path

    # Parse command line value to out_file
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
        stats_data = []
                    
        for folder in folders:  
            print("Generating stats data for ", folder)                          
            sources = get_stats(folder)  

            folder_name = folder.split(os.sep)[-1]        
            data = [folder_name]
            for index in range(len(sources)):
                data.append(sources[index])

            stats_data.append(data)  

            print("Processed stats data for ", folder)

        

        write_csv_file(out_file, stats_data)                        
        
    print("Generating Lat Lon Stats done.")


    
