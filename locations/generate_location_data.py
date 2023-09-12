import os
import argparse
import math
from math import isnan

import json
import pandas as pd
import numpy as np

from geopy.geocoders import Nominatim
from functools import lru_cache


COLUMN_NAMES = ['batch', 'country', 'city', 'lat', 'lon', 'time offset']


@lru_cache(maxsize=None)
def get_lat_lon(city):
    geolocator = Nominatim(user_agent="geoapiExercises")    
    lat_lon = geolocator.geocode(city)    
    lat = lat_lon.latitude    
    lon = lat_lon.longitude

    return lat, lon

def read_csv_file(csv_file):
    csv_data = []
    df = pd.read_csv(csv_file, index_col=False)        
    no_entries = len(df)    
    print("No. of Entries in CSV file = ", no_entries)
    col_names = df.columns
    #print("Column Names = ", col_names)

    # Assumption here, column - 0 is the directory
    # column - 2 is the city
    # column - 3 is the country
    # colum - 12 is the time offset

    for index, row in df.iterrows():
        path = row[col_names[0]]
        city = row[col_names[2]] 
        country = row[col_names[3]]        
        time_offset = row[col_names[12]]         
        if isnan(time_offset):
            time_offset = 0
        #print(time_offset)                 
        row_data = [path, country, city, time_offset ]
        
        csv_data.append(row_data)      

    return csv_data

def write_json_data(json_file, data):

    df = pd.DataFrame(data, columns=COLUMN_NAMES) 
    #df.to_json(json_file, orient='records', lines = True)
    df.to_json(json_file, orient='records', indent=2)

    #with open(json_file, "w") as file:
        #json.dump(data, file)
    
    return

def generate_dict_data(row_data):
    batch = row_data[0]
    
    country = row_data[1]
    city = row_data[2]   
    lat, lon = get_lat_lon(city)
    offset = row_data[3]

    data_dict = {
        COLUMN_NAMES[0]: batch,        
        COLUMN_NAMES[1]: country,
        COLUMN_NAMES[2]: city,
        COLUMN_NAMES[3]: lat,
        COLUMN_NAMES[4]: lon,
        COLUMN_NAMES[5]: offset
    }    
    return data_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Parse csv file and then update json file.")
    
    # Parse input csv file
    parser.add_argument("--csv_file", type=str, 
                        help="Input file in csv.")
    
    # Parse json file
    parser.add_argument("--json_file", type=str, 
                        help="Json file.")
    
    # Parse the command line arguments
    args = parser.parse_args()

    # Read the command line parameter to Input file
    csv_file = args.csv_file

    # Read the command line parameter to no bins
    json_file = args.json_file

    is_process = True

    if (os.path.exists(csv_file)):
        ext = os.path.splitext(csv_file)[1]
        #print(ext)
        if ext == ".csv":
            csv_file = os.path.abspath(csv_file)
            print("Input csv file = ", csv_file)
        else:
            is_process = False
            print("Input file csv file, {0} does not have extension .csv.".
                format(csv_file))     
    else:
        print (f"can't find {csv_file}")
        is_process = False

    if is_process:
        if (os.path.exists(json_file)):
            ext = os.path.splitext(json_file)[1]            
            if ext == ".json":
                json_file = os.path.abspath(json_file)
                print("Input/output json file = ", json_file)
            else:
                is_process = False
                print("Input/output file json file, {0} does not have " 
                      "extension . json. ".format(json_file))     
        else:
            json_file = os.path.abspath(json_file)
            print("Input/output json file = ", json_file)
            with open(json_file, 'w') as f:
                print("Created empty json file, {0} created."
                        .format(json_file))
        
    if is_process:  
        print("Process Further.") 
        csv_data = read_csv_file(csv_file)        
        no_rows = len(csv_data)
        print("No. of Rows = ", no_rows)

        #json_data = read_json_file(json_file)
        #print(json_data[0])
        data_dicts = []
        for index in range(no_rows):
            print (f"processing row {index}")
            row_data = csv_data[index]            
            if isinstance(row_data[0], str):
                data_dict = generate_dict_data(row_data)                
                data_dicts.append(data_dict)

        print("No. Data Dicts = ", len(data_dicts))
        write_json_data(json_file, data_dicts)
        
        

        
    print("Generating Location Tool done.")




'''
def read_json_file(json_file):
    

    return df
df = read_json_file(json_file)

        for index, row in df.iterrows():
            print(row[0])
            break
'''