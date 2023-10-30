import os
import glob
import argparse
import json
import math

from typing import Dict
from typing import Union
from typing import Optional
from typing import Tuple

from datetime import timedelta
from datetime import datetime

import distutils

import gpxpy
import fitdecode

import pandas as pd
import exifread

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

FIELD_NAMES = ['Date', 'Time', 'Latitude', 'Longitude']

def time_sum(time_original, time_offset): 
    """
    Calculates time in the hh:mm:ss format    
    """
    is_positive = False
    (h, m, s) = str(time_original).split(':')
    # Crete a time
    time_1 = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    (h, m, s) = str(time_offset).split(':')
    time_2 = timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    add_time = time_1 + time_2

    if str(add_time).find(',') != -1:        
        is_positive = True
        add_time = str(add_time).split(",")[1]
        add_time = add_time.strip()

    add_time = datetime.strptime(str(add_time), "%H:%M:%S").time()        

    return is_positive, add_time

def time_sub(time_original, time_offset): 
    """
    Calculates time from list of time hh:mm:ss format
    """
    is_negative = False
    (h, m, s) = str(time_original).split(':')
    # Crete a time
    time_1 = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
    (h, m, s) = str(time_offset).split(':')
    time_2 = timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    sub_time = time_1 - time_2 
    
    if str(sub_time).find('-') != -1:        
        is_negative = True
        sub_time = str(sub_time).split(",")[1]
        sub_time = sub_time.strip()
    
    sub_time = datetime.strptime(str(sub_time), "%H:%M:%S").time()    
    return is_negative, sub_time

def inc_one_day(date_stamp):
    new_date_stamp = "  "
    new_date_stamp = datetime.strptime(date_stamp, '%Y:%m:%d')
    new_date_stamp = new_date_stamp + timedelta(days = 1) 
    new_date_stamp = new_date_stamp.date()            
    new_date_stamp = datetime.strftime(new_date_stamp, '%Y:%m:%d')          
    return new_date_stamp

def dec_one_day(date_stamp):
    new_date_stamp = "  "
    new_date_stamp = datetime.strptime(date_stamp, '%Y:%m:%d')
    new_date_stamp = new_date_stamp - timedelta(days = 1) 
    new_date_stamp = new_date_stamp.date()            
    new_date_stamp = datetime.strftime(new_date_stamp, '%Y:%m:%d')          
    return new_date_stamp

def dec_one_second(time_str):
    # Split the time (in str) to hours, minutes, and seconds
    (h, m, s) = str(time_str).split(':')

    # Crete a time
    time_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    # Decrement time by one second
    time_dec =  time_time - timedelta(hours=0, minutes = 0, seconds = 1)   
    time_dec = str(time_dec)
    if (',' in time_dec):
        time_dec_split = time_dec.split(',')
        time_dec = time_dec_split[1].strip()

    time_dec = datetime.strptime(str(time_dec), "%H:%M:%S").time()

    return time_dec

def inc_one_second(time_str):
    # Split the time (in str) to hours, minutes, and seconds
    (h, m, s) = str(time_str).split(':')

    # Crete a time
    time_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    # Increment time by one second
    time_inc =  time_time + timedelta(hours=0, minutes = 0, seconds = 1)   
    time_inc = str(time_inc)
    if (',' in time_inc):
        time_inc_split = time_inc.split(',')
        time_inc = time_inc_split[1].strip()

    time_inc = datetime.strptime(str(time_inc), "%H:%M:%S").time()
    return (time_inc)

def get_time_sec(time_time):
    # Split the time (in str) to hours, minutes, and seconds
    (h, m, s) = time_time.split(':')

    # Crete a time
    time_time_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    # Convert to total seconds
    time_sec = time_time_time.total_seconds()

    return time_sec

def get_interpolation(curr_time, prev_data, next_data):
    # Get the interpolation for lat
    lat = prev_data[1] + (curr_time - prev_data[0]) * \
            ((next_data[1] - prev_data[1])/(next_data[0] - prev_data[0]))
    
    # Get the interpolation for lon
    lon = prev_data[2] + (curr_time - prev_data[0]) * \
            ((next_data[2] - prev_data[2])/(next_data[0] - prev_data[0]))
    
    return lat, lon

def track_get_date_time(data):  
    # The data is in format of Y:M:D H:M:S

    # convert datetime to string format
    date_time = data.strftime("%Y:%m:%d %H:%M:%S")    

    # Split the datetime with space 
    data_time_split = date_time.split(" ")

    # Assign date split
    data_date = data_time_split[0]

    # Assign time split
    data_time = data_time_split[1]

    return data_date, data_time

def form_gps_data(datestamp, timestamp, lat, lon):  
    # Create a data dictionary and return  
    data = {        
        FIELD_NAMES[0]: datestamp,
        FIELD_NAMES[1]: timestamp, 
        FIELD_NAMES[2]: lat, 
        FIELD_NAMES[3]: lon                                       
        }
    
    return data

def get_track_data(date_time, lat, lon):
    # Get the date and time and date_time data
    track_date, track_time = track_get_date_time(date_time)    

    # Create track data dictionary    
    track_data = form_gps_data(track_date, track_time, lat, lon)

    return track_data

# Parse the gpx file
def parse_gpx(route_file):
    # Open the gpx file
    with open(route_file) as f:
        # parse the gpx file
        gpx = gpxpy.parse(f)
        #print("No. of Tracks  =", len(gpx.tracks))

        # Book Keeping for track data
        track_datas = []

        # Parse each track
        for track in gpx.tracks:
            #print("No. of Segments =", len(track.segments))
            for segment in track.segments:
                #print("No. of Points = ", len(segment.points))
                
                # Parse each point in the segment points
                for point in segment.points:                    
                    # Get the data, time, lat, lon data for each point
                    track_data = get_track_data(point.time, 
                                                point.latitude,
                                                point.longitude)                    
                    
                    track_datas.append(track_data)                      
        
        gpx_df = pd.DataFrame(track_datas, columns = FIELD_NAMES)
        #print("No. of points in track = ", len(gpx_df.index))                 

    return gpx_df

def get_fit_point_data(frame: fitdecode.records.FitDataMessage):        
     # If the frame does not have any latitude or longitude data. 
     # We will ignore these frames in order to keep things

    values = [] 
    
    if (frame.has_field('position_lat') and frame.has_field('position_long')
            and frame.has_field('timestamp')):   
                         
        lat = frame.get_value('position_lat') / ((2**32) / 360)
        lon = frame.get_value('position_long') / ((2**32) / 360)            
        datetime = frame.get_value('timestamp')  
        values.append(datetime)
        values.append(lat)
        values.append(lon)
       
    return values 

# Parse the fit track file
def parse_fit(route_file):
    # Open the route file
    track_datas = []         
    with fitdecode.FitReader(route_file) as fit_file:
        for frame in fit_file:             
            if isinstance(frame, fitdecode.records.FitDataMessage):
                # if the frame name is record
                if frame.name == 'record':
                    # Get the datetime, lat, lon from the frame
                    
                    values = get_fit_point_data(frame)
                    if len(values) >0:                        
                        datetime = values[0]
                        lat = values[1]
                        lon = values[2]
                        # Get the track data
                        track_data = get_track_data(datetime, lat, lon)                    
                        track_datas.append(track_data)               
                        
                        
    fit_df = pd.DataFrame(track_datas, columns = FIELD_NAMES)
    #print("No. of points in track = ", len(fit_df.index))
    #print(fit_df.head(100))
    return fit_df

def parse_route_files(input_path):
    route_files = []

    # Get the all the fit and gpx files
    for exn in ("**.fit", "**.gpx" ):
        route_files.extend(sorted(glob.glob(input_path + "/" + exn)))
    
    # Create a data frame with columns and no data
    df = pd.DataFrame(columns = FIELD_NAMES)  

    if (len(route_files) > 0):
        print("No. of Route Files = ", len(route_files))            

        # Parse each route file
        for route_file in route_files:            

            # Parse the gpx route file
            if route_file.endswith(".gpx"):
                gpx_df = parse_gpx(route_file)

                # Concatenate individual route files data to main data frame
                df = pd.concat([df, gpx_df])

                #print("No. of Rows in route data frame = ", len(gpx_df.index))                  
            
            # Parse the fit route file
            if route_file.endswith(".fit"):
                fit_df = parse_fit(route_file)

                # Concatenate individual route files data to main data frame
                df = pd.concat([df, fit_df])
                #print("No. of Rows in route data frame = ", len(fit_df.index))

            print("Processed {0} file.".format(route_file))
    #print(df.head(100))
    return df  

def convert_time_stamp(time_stamp):
    (h, m, s) = str(time_stamp).split(':')
    if (int(h)) < 10:
        h = "0" + h
    if (int(m)) < 10:
        m = "0" + m
    if (int(s)) < 10:
        s = "0" + s
    
    time_str = h + ":" + m + ":" + s

    return time_str

def get_df_row_data(df, date_stamp, time_stamp):
    
    # Get the data frame based on the date stamp       
    new_df = df[df[FIELD_NAMES[0]] == str(date_stamp)]    

    # From the new data frame, get the location(s) based on the time stamp
    row_data = new_df.loc[new_df[FIELD_NAMES[1]] == str(time_stamp)]    

    # Convert to the normal list values (single horizontal row)
    row_data = row_data.values.flatten().tolist()    

    return row_data


def conv_time_stamp(timestamp):    
    time_stamp = str(timestamp[0]) + ":" + \
                str(timestamp[1]) + ":" + str(timestamp[2])
    return time_stamp

def conv_timeoffset(offset):
    #hours = offset / 60
    #minutes = offset % 60
    #hours = math.floor(hours)

    is_negative = False

    if (offset < 0):
        is_negative = True
        offset = abs(offset)

    hours, minutes = divmod(offset, 60)

    if (is_negative):
        hours = hours * -1

    if hours >= 0 and hours < 10:
        hours = "0" + str(hours)
    elif hours < 0:
        hours = "-0" + str(abs(hours))
    else:
        hours = str(hours)

    if minutes < 10:
        minutes = "0"+ str(minutes)
    else:
        minutes = str(minutes)

    time_offset = hours + ":"+ minutes + ":00"

    return time_offset 

def get_prev_row_data(df, date_org, utc_time):
    # Get the data frame data for the previous second until 
    # data found or loop 5 minutes
    no_fields = len(FIELD_NAMES)
    prev_utc_time = utc_time
    prev_row_data = None
    for index in range (300):
        # Get the data frame for the previous second
        prev_utc_time = dec_one_second(prev_utc_time)        
        prev_row_data = get_df_row_data(df, date_org, prev_utc_time)         
        if len(prev_row_data) == no_fields:
            break   
    
    return prev_row_data             

def get_next_row_data(df, date_org, utc_time):
    # Get the data frame data for the previous second until 
    # data found or loop 5 minutes
    no_fields = len(FIELD_NAMES)
    next_utc_time = utc_time
    next_row_data = None
    for index in range (300):
        # Get the data frame for the previous second
        next_utc_time = inc_one_second(next_utc_time)                        
        next_row_data = get_df_row_data(df, date_org, next_utc_time) 
        
        if len(next_row_data) == no_fields:
            break   

    return next_row_data     

def get_interpolated_lat_lon(df, date_org, utc_time):
    is_int = False
    lat = float(0)
    lon = float(0)
    no_fields = len(FIELD_NAMES)

    prev_row_data = get_prev_row_data(df, date_org, utc_time)        
    next_row_data = get_next_row_data(df, date_org, utc_time)
    
    # TODO: if there is no prev_row_data or 
    # if there is no next_row_data or
    # if prev_row_data has more than one entry
    #if next_row_data has more than one entry

    #if (prev_row_data != None) and (next_row_data != None):

    if (len(prev_row_data) == 0) and \
       (len(next_row_data) == no_fields):
        lat = next_row_data[2]
        lon = next_row_data[3]
        is_int = True

    if (len(prev_row_data) == no_fields) and \
       (len(next_row_data) == 0):
        lat = prev_row_data[2]
        lon = prev_row_data[3]
        is_int = True

    if (len(prev_row_data) > no_fields) and  \
       (len(next_row_data) == no_fields):
        lat, lon = get_gps_info_rows(prev_row_data)
        prev_time_sec = get_time_sec(prev_row_data[1])
        next_time_sec = get_time_sec(next_row_data[1])
        cur_time_sec = get_time_sec(str(utc_time))

        # Make data for previous and next
        prev_data = [prev_time_sec, lat, lon]
        next_data = [next_time_sec, next_row_data[2], next_row_data[3]]            
        # Interpolate lat, lon
        lat, lon = get_interpolation(cur_time_sec, prev_data, next_data)
        is_int = True

    if (len(prev_row_data) == no_fields) and  \
       (len(next_row_data) > no_fields):
        lat, lon = get_gps_info_rows(next_row_data)
        prev_time_sec = get_time_sec(prev_row_data[1])
        next_time_sec = get_time_sec(next_row_data[1])
        cur_time_sec = get_time_sec(str(utc_time))

        # Make data for previous and next
        prev_data = [prev_time_sec, prev_row_data[2], prev_row_data[3]]
        next_data = [next_time_sec, lat, lon]            
        # Interpolate lat, lon
        lat, lon = get_interpolation(cur_time_sec, prev_data, next_data)
        is_int = True

    if (len(prev_row_data) > no_fields) and  \
       (len(next_row_data) > no_fields):        
        prev_time_sec = get_time_sec(prev_row_data[1])
        next_time_sec = get_time_sec(next_row_data[1])
        cur_time_sec = get_time_sec(str(utc_time))

        # Make data for previous and next
        lat, lon = get_gps_info_rows(prev_row_data)
        prev_data = [prev_time_sec, lat, lon]

        lat, lon = get_gps_info_rows(next_row_data)
        next_data = [next_time_sec, lat, lon]            
        # Interpolate lat, lon
        lat, lon = get_interpolation(cur_time_sec, prev_data, next_data)
        is_int = True


    if (len(prev_row_data) == no_fields) and \
       (len(next_row_data) == no_fields):
        # Get the seconds time for previous, next, and current UTC time
        prev_time_sec = get_time_sec(prev_row_data[1])
        next_time_sec = get_time_sec(next_row_data[1])
        cur_time_sec = get_time_sec(str(utc_time))

        # Make data for previous and next
        prev_data = [prev_time_sec, prev_row_data[2], prev_row_data[3]]
        next_data = [next_time_sec, next_row_data[2], next_row_data[3]]            
        # Interpolate lat, lon
        lat, lon = get_interpolation(cur_time_sec, prev_data, next_data)
        is_int = True

    if (len(prev_row_data) == 0) and \
       (len(next_row_data) == 0):
        lat = float(0)
        lon = float(0)
        is_int = False

    return is_int, lat, lon    

def get_gps_info_rows(row_data):
    # Get the no. of elements in the row data                  
    no_elements = len(row_data)

    # initialize lat and lon values
    lat = float(0)
    lon = float(0)

    no_fields = len(FIELD_NAMES)

    # For each set of data, get the lat and lon 
    for index in range(0, no_elements, no_fields):
        #print(index)
        lat = lat + row_data[index + 2]
        lon = lon + row_data[index + 3]
    
    # Take the average of lot and lon
    no_rows = (no_elements / no_fields)
    lat = lat / no_rows
    lon = lon / no_rows                   

    return lat, lon

def create_gps_info(source, date_stamp, time_stamp, lat, lon):
    gps_info = []
    gps_info.append(source)
    gps_info.append(date_stamp)
    gps_info.append(time_stamp)
    gps_info.append(lat)
    gps_info.append(lon)

    return gps_info

def get_time_offset(lat, lon):
    timezone_obj = TimezoneFinder()
  
    # returns 'Europe/Berlin'
    time_zone = timezone_obj.timezone_at(lng=lon, lat=lat)        
    time_zone_now = datetime.now(pytz.timezone(str(time_zone)))    
    time_offset = time_zone_now.utcoffset().total_seconds()
    time_offset = time_offset/60
    return time_offset

def get_gps_info(image_file):
    gps_info = []
    source_type = None
    with open(image_file, 'rb') as src:
         tags = exifread.process_file(src, details=False)

    '''
    for tag in tags.keys():
        print(tag, tags[tag])
    '''
    time_stamp = None
    date_stamp = None

    for tag in tags.keys():
        if tag == 'GPS GPSTimeStamp':
            time_stamp = exifread.utils.ord_(tags['GPS GPSTimeStamp']).values
            time_stamp = conv_time_stamp(time_stamp)            
        if tag == 'GPS GPSDate':    
            date_stamp = exifread.utils.ord_(tags['GPS GPSDate']).values

    if time_stamp == None:        
        tag = 'EXIF DateTimeOriginal'
        if (tag in tags.keys()):
            datetime_original = exifread.utils.ord_(tags[tag]).values

            # Split the Date and Time
            date_time_split = datetime_original.split(" ")
            time_stamp = date_time_split[1]


    if time_stamp and date_stamp:
        lat, lon = exifread.utils.get_gps_coords(tags)
        source = "camera"
        gps_info = create_gps_info(source, date_stamp, time_stamp, lat, lon)        
        source_type = 0

    return source_type, gps_info
        
def get_gps_info_df(image_file, df, main_lat = 0.0, main_lon = 0.0, 
        main_time_offset = 0):
    gps_info = []
    no_traces = len(df)

    #print("Image File =", image_file)    
    #print("No. traces = ", no_traces)

    tags = []
    with open(image_file, 'rb') as src:
        try:
            tags = exifread.process_file(src, details=True)
        except:
            print("Probalem while reading EXIF tag with file,",src)

    #for tag in tags.keys():
    #    print(tag, tags[tag])

    if (len(tags) == 0):
        source = "coarse"
        gps_info = create_gps_info(source, "", "", main_lat, main_lon)
        source_type =2
        return source_type, gps_info

    # Get the datetime original and data type is string
    tag = 'EXIF DateTimeOriginal'
    datetime_original = exifread.utils.ord_(tags[tag]).values
    # print("Date Time original :", datetime_original)    
    
    # Split the Date and Time
    date_time_split = datetime_original.split(" ")
    date_original = date_time_split[0]
    time_original = date_time_split[1]     

    if no_traces == 0:
        source = "coarse"
        gps_info = create_gps_info(source, str(date_original), 
                    str(time_original), main_lat, main_lon)                       
        source_type = 2
        return source_type, gps_info

    
    # Get the Offset Time Original data
    is_offset = False
    if main_time_offset != 0.0:
        #print("Consider Manual Offset")
        time_offset = conv_timeoffset(main_time_offset)
        #print(time_offset)
        is_offset = True

    if not is_offset:
        for tag in tags.keys():
            if tag == 'MakerNote Tag 0x0035':
                time_offset = exifread.utils.ord_(tags[tag]).values           
                #print(time_offset)
                time_offset = conv_timeoffset(time_offset[1]) 
                #print("Maker Note Offset = ", time_offset)
                is_offset = True
                break

            if tag == 'EXIF OffsetTimeOriginal':            
                time_offset = exifread.utils.ord_(tags[tag]).values
                # Add 00 to make consistent with second value.
                time_offset = time_offset + ":00"
                #print("EXIF Offset = ", time_offset)
                is_offset = True
                break

    if not is_offset:
        source = "coarse"
        gps_info = create_gps_info(source, str(date_original),
                    str(time_original), main_lat, main_lon)
        source_type = 2
        return source_type, gps_info
    '''
    # There is no offset
    if not is_offset:
        time_offset = get_time_offset(main_lat, main_lon)        
        time_offset = conv_timeoffset(int(time_offset))
        #print("Lat, Lon Time Offset = ", time_offset)
        #print(time_offset) 

    '''
    #print(time_offset, is_offset)
    #time_offset = conv_timeoffset(main_time_offset)
    #print(time_offset)    
    # Get the UTC by adding or substracting time original and offset            
    if (time_offset[0] == "-"):
        time_offset = time_offset[1:]                                    
        is_positive, utc_time = time_sum(time_original, time_offset)
        if (is_positive):
            date_original = inc_one_day(date_original)
    else:                        
        is_negative, utc_time = time_sub(time_original, time_offset)        
        if (is_negative):  
            date_original = dec_one_day(date_original)            

    #print(date_original, utc_time)
    # Get the dataframe row for the date and UTC
    row_data = get_df_row_data(df, date_original, utc_time)
    no_fields = len(FIELD_NAMES)

     # If only one row found
    if len(row_data) == no_fields:                    
        #print(row_data)
        source = "track"   
        gps_info  = create_gps_info(source, row_data[0], row_data[1], 
                        row_data[2], row_data[3])        
        source_type = 1
    elif len(row_data) == 0:
        is_int, lat, lon = get_interpolated_lat_lon(df, date_original, utc_time)   
        if is_int: 
            source = "track"   
            gps_info  = create_gps_info(source, str(date_original),
                                str(utc_time), lat, lon)                                   
            source_type = 1
        else:  
            source = "coarse"   
            gps_info  = create_gps_info(source, str(date_original), 
                            str(utc_time), main_lat, main_lon)                       
            source_type = 2
    else:
        lat, lon = get_gps_info_rows(row_data)
        source = "track"   
        gps_info  = create_gps_info(source, str(date_original), str(utc_time), 
                        lat, lon)        
        source_type = 1        
    return source_type, gps_info

def parse_json_file(json_file, root_path):
    json_data = []
    df = pd.read_json(json_file)

    for index, row in df.iterrows():
        src_path = os.path.join(root_path, "photos", row[0])
        dest_path = os.path.join(root_path,"metadata_location", row[0])
        
        row_data = [src_path,
                    dest_path,
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5]
                    ]
        
        json_data.append(row_data)
    
    return json_data

def get_location_data(gps_info, country, city):
    # Create a dictionary value and return
    location_data = {                        
        "Source": gps_info[0],
        FIELD_NAMES[0]: gps_info[1],
        FIELD_NAMES[1]: gps_info[2],
        FIELD_NAMES[2]: gps_info[3],
        FIELD_NAMES[3]: gps_info[4],        
        "Country": country,
        "City": city                        
        }
    
    return location_data

def write_location(image_file, output_path, data):
    # Get the base file of the image file
    base_name = os.path.basename(image_file)    

    # Get the file name and file extension from the base file
    file_name, ext = os.path.splitext(base_name)    

    # Create the destination file
    dest_file = os.path.join(output_path, file_name + ".json")        

    # Open the destination in write mode and then write the data
    # in JSON file
    with open(dest_file, "w") as outfile:
        json.dump(data, outfile)
        #print("Generated {0} file.".format(dest_file))

    return 

def generate_location(data):
    src_path = data[0]
    dest_path = data[1]
    country = data[2]
    city = data[3]
    lat = float(data[4])
    lon = float(data[5])
    time_offset = int(data[6])
    print(data)
  
    dest_path = os.path.abspath(dest_path)
    print("Destination Path = ", dest_path)
    if not os.path.exists(dest_path): 
        os.makedirs(dest_path)
        print("Created Meta data location path, ", dest_path)

    if os.path.exists(dest_path):
        # Get the image files:
        image_files = []
        for exn in ("**.jpg", "**.JPG"):
            image_files.extend(sorted(glob.glob(src_path+"/"+exn)))
        
        no_images = len(image_files)
        print("No. of Image files = ", no_images)

        df = parse_route_files(src_path)
        no_traces = len(df)
        print("No. of Traces = ", no_traces)

        '''
        trace_file = os.path.join(dest_path, "traces.csv")
        if not os.path.exists(trace_file):
            df = parse_route_files(src_path)
            no_traces = len(df)
            print("No. of Traces = ", no_traces)
            if no_traces > 0:
                df.to_csv(trace_file, index=False)
        else:
            df = pd.read_csv(trace_file, index_col=False)        
            no_traces = len(df)
            print("No. of Traces = ", no_traces)
        '''
        
        # Differet souce type counters.               
        source_camera = 0
        source_track = 0
        source_coarse = 0

        index = 0
        for image_file in image_files: 
            #print(image_file)       
            source_type, gps_info = get_gps_info(image_file)         
            if len(gps_info) == 0:
                source_type, gps_info = get_gps_info_df(image_file, df, lat, 
                        lon, time_offset)

            location_data = get_location_data(gps_info, country, city)

            if source_type == 0:
                source_camera = source_camera + 1
            elif source_type == 1:
                source_track = source_track + 1                    
            elif source_type == 2:
                #print("No GPS data for image: ", image_file)
                source_coarse = source_coarse + 1

            #print(image_file, location_data)
            # Write the json file in the output path
            write_location(image_file, dest_path, location_data)  
            index = index + 1
            print("Processed {0} out of {1} images.". 
                format(index, no_images), end='\r')

        # print the counters
        print("\nTotal number of images = ", no_images)
        print("Source type, {0} and no. json files = {1}."
                .format("camera",source_camera))
        print("Source Type, {0} and no. json files = {1}."
                .format("track", source_track))
        print("Source Type, {0} and no. json files = {1}."
                .format("coarse", source_coarse))
                                                        
        if ((source_camera + source_track + source_coarse) != no_images):
            print("Json files are not correctly generated.")
                
    return
    
if __name__ == "__main__":    

    parser = argparse.ArgumentParser(
                description="Generate Location Data from route files.")

    # Parse Images data path
    parser.add_argument("--root_path", type=str,default="",
                        help="root path name.")

    # Parse Image data path
    parser.add_argument("--image", type=str, default = "",
                        help="Image file path.")
    
    # Parse Config file path
    parser.add_argument("--json_file", type=str, default = "",
                        help="Json file path.")
    
    # Parse city
    parser.add_argument("--city", type=str, nargs='+', default = "",
                        help="City of the images.")

    # Overwirte data
    parser.add_argument("--is_overwrite", default = False, 
            type=lambda x: bool(strtobool(str(x).strip()))) 
    
    args = parser.parse_args()

    # Parse command line value to root path
    root_path = args.root_path

    # Parse command line value to image file
    image_file = args.image    

    # Parse command line value to Json file
    json_file = args.json_file

    # Parse command line value to City file
    city = args.city
    city = " ".join(city)

    is_overwrite = args.is_overwrite
    print("Is Overwrite =", is_overwrite)

    is_process = True

    if is_process:
        print("Process Futher.")
        gps_info = []
        if len(image_file) > 0:
            if not os.path.exists(image_file):                            
                print("Image file, {0} does not exists.".format(image_file)) 
                is_process = False
            
            if is_process:
                print("Process {0} file.".format(image_file))                
                source_type, gps_info = get_gps_info(image_file) 
                if len(gps_info) > 0:               
                    location_data = get_location_data(gps_info, "Temp", city)
                    print(location_data)                

        if len(gps_info) == 0: 
            if len(image_file) > 0:
                if not os.path.exists(image_file):                            
                    print("Image file, {0} does not exists."
                        .format(image_file)) 
                    is_process = False 
            else:
                is_process = False 
            if len(root_path) > 0:
                if not os.path.exists(root_path):                            
                    print("Routes path, {0} does not exists."
                        .format(root_path)) 
                    is_process = False 
            else:
                is_process = False     
            if is_process:
                print("Process Image and Trace files.")
                trace_file = os.path.join(root_path, "traces.csv")
                if not os.path.exists(trace_file):
                        df = parse_route_files(root_path)
                        no_traces = len(df)
                        print("No. of Traces = ", no_traces)
                        if no_traces > 0:
                            df.to_csv(trace_file)
                else:
                    df = pd.read_csv(trace_file)
                    no_traces = len(df)
                    print("No. of Traces = ", no_traces)                    
                    
                print("Processing {0} image.".format(image_file))
                # getting Latitude and Longitude
                geolocator = Nominatim(user_agent="geoapiExercises")
                lat_lon = geolocator.geocode(city)
                lat = lat_lon.latitude
                lon = lat_lon.longitude
                source_type, gps_info = get_gps_info_df(image_file, df, lat, lon)
                #print(gps_info)
                location_data = get_location_data(gps_info, "Temp", city)
                print(location_data)                

        if len(json_file) > 0 and len(root_path) > 0:
            print("Both root path and JSON file.")
            is_process = True
            if not os.path.exists(root_path):                            
                    print("Root path, {0} does not exists."
                        .format(root_path)) 
                    is_process = False 
            if not os.path.exists(json_file):                            
                    print("Json file, {0} does not exists."
                        .format(json_file)) 
                    is_process = False 
            if is_process:
                root_path = os.path.abspath(root_path)
                print("Root path =", root_path)

                json_file = os.path.abspath(json_file)
                print("Json File = ", json_file)

                json_data = parse_json_file(json_file, root_path)
            
                data_len = len(json_data)
                # Consider 2nd row onwards, 1st row is header
                for index in range(data_len):
                    row_data = json_data[index]
                    print(row_data)
                    print("Generating location data for ", row_data[0])
                    generate_location(row_data)
                    print("\nGenerated location data for ", row_data[0])
                
        
    print("Generating Location Tool done.")

#https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_gpx.py
#https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_fit.py
#https://towardsdatascience.com/parsing-fitness-tracker-data-with-python-a59e7dc17418
#https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354
# http://academic.brooklyn.cuny.edu/geology/leveson/core/linksa/decimalconvert.html


