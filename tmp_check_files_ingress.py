import os
import glob
import argparse

if __name__ == "__main__":
    # print("Welcome to Check Files Tool.")

    parser = argparse.ArgumentParser(
        description="Check jpgs, raw and fit files.")

    # Parse Data path
    parser.add_argument("--input_path", type=str,
                        help="Data path name.")

    # Parse Image file extension
    parser.add_argument("--image_ext", type=str, default="jpg",
                        help="Images File Extension.")

    # Parse Raw file extension
    parser.add_argument("--raw_ext", type=str, default="NEF",
                        help="Images File Extension")

    # Parse Route File extension
    parser.add_argument("--route_ext", type=str, default="fit",
                        help="Route Files Extension")

    # Parse the command line arguments
    args = parser.parse_args()

    # Read the command line parameter to data path
    input_path = args.input_path
    print("Input images path is ", input_path)

    # Read the command line parameter to image extension
    image_extn = args.image_ext
    print("Images Extension is ", image_extn)

    # Read the command line parameter to image extension
    raw_extn = args.raw_ext
    print("Raw images Extension is ", raw_extn)

    # Read the command line parameter to image extension
    route_extn = args.route_ext
    print("Route Files exension is ", route_extn)

    # Check whether input file exists or not
    is_process = False

    # Check whether images path exists
    if os.path.exists(input_path):
        is_process = True
    else:
        print("Input Data path {0} does not exist.".format(input_path))

    if (is_process):
        print("Process Further.")

        # Get all Image files
        wild_character = "/*." + image_extn
        image_files = glob.glob(input_path + wild_character)
        no_images = len(image_files)
        print("No. of Image files(*.{0}) = {1}".format(image_extn, no_images))

        # Get all Raw files
        wild_character = "/*." + raw_extn
        raw_files = glob.glob(input_path + wild_character)
        no_raws = len(raw_files)
        print("No. of Raw files(*.{0}) = {1}".format(raw_extn, no_raws))

        # Get all Raw files
        wild_character = "/*." + route_extn
        route_files = glob.glob(input_path + wild_character)
        no_routes = len(route_files)
        print("No. of Route files(*.{0}) = {1}".format(route_extn, no_routes))

        total_files = no_images + no_raws + no_routes
        print("Total Number of Files = ", total_files)

        matched = 0

        for image_file in image_files:
            image_base_name = os.path.basename(image_file)
            file_name, file_extension = os.path.splitext(image_base_name)
            raw_file_name = os.path.join(input_path, file_name + "." + raw_extn)
            if (not os.path.isfile(raw_file_name)):
                print("Raw file does not exist for", image_base_name)
            else:
                matched = matched + 1

        if (matched != len(image_files)):
            for raw_file in raw_files:
                raw_base_name = os.path.basename(raw_file)
                file_name, file_extension = os.path.splitext(raw_base_name)
                img_file_name = os.path.join(input_path, file_name + "." + image_extn)
                if (not os.path.isfile(img_file_name)):
                    print("Image file does not exist for", raw_base_name)

        if (matched == len(image_files)):
            print("All files are matched.")

    print("Checking files Tool done.")

'''
if (is_process):
        print("Process furhter.")

        create_xls_file(input_path)
        # Get the Excel Sheet in the png images file path
        output_excel = glob.glob(glob.escape(input_path) + "/*.xlsx")[0] 
        print("The Updated Excel Sheet is", output_excel)

        # Get Input Excel sheet data frame
        i_df = get_df(input_excel) 

        # Get Output Excel sheet data frame
        o_df = get_df(output_excel) 

        # Get input Excel sheet JPEGS list
        jpeg_files = get_col_data(i_df, 3)

        # Get the output Excel sheet URLs
        o_urls = get_col_data(o_df, 1)

        jpg_files = []
        for jpg_file in jpeg_files: 
            jpg_base_name = os.path.basename(jpg_file) 
            jpg_files.append(jpg_base_name)        

        # Get the input directory PNG files
        png_files = glob.glob(glob.escape(input_path) + "/*.png")
        print("Number of PNG Files are", len(png_files))

        for png_file in png_files:
            png_base_name = os.path.basename(png_file)
            file_name, file_extension = os.path.splitext(png_base_name)
            jpg_file_name = file_name + ".jpg"

            try:
                i_index = jpg_files.index(jpg_file_name)

                # Get the row data of f_index in the input Excel File
                i_data_row = i_df.iloc[i_index].to_list()

                # Get the URL from the input 
                url = i_data_row[1]            
                try:
                    url_index = o_urls.index(url)
                    #print("Already exists", png_base_name)
                except ValueError:
                    o_urls.append(url)
                    o_data_row = [len(o_df.index) + 1, url, i_data_row[2], png_base_name, i_data_row[4]]
                    o_df.loc[len(o_df.index)] = o_data_row
            except:
                print("Did not find {0} file.".format(jpg_file_name))
                splide_part = jpg_file_name.split("_")
                part_2 = ''
                for element in range(1, len(splide_part)):
                    part_2 = part_2 + splide_part[element] + "_"

                part_2 = part_2[:-1]
                url = "https://live.staticflickr.com/" + splide_part[0] + "/" + part_2 

                try:
                    url_index = o_urls.index(url)
                    #print("Already exists", png_base_name)
                except ValueError:
                    o_urls.append(url)
                    o_data_row = [len(o_df.index) + 1, url, "", png_base_name, ""]
                    o_df.loc[len(o_df.index)] = o_data_row

        appended_data = pd.DataFrame()
        appended_data = pd.concat([appended_data, o_df], axis = 0)
        appended_data.to_excel(output_excel, index=False)    


'''




