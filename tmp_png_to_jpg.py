from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor


"""
move renders from png to jpg
"""

def convert_png_to_jpg(png_path, jpg_path):

    print (f"converting {png_path} to {jpg_path}")
    # Open the PNG image
    img = Image.open(png_path)

    # Convert RGBA to RGB if the image has an alpha channel
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Save as JPEG
    img.save(jpg_path, 'JPEG', quality=90)


def convert_all_png_to_jpg(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all PNG files in the input folder
    png_files = [filename for filename in os.listdir(input_folder) if filename.endswith(".png")]

    # Use ThreadPoolExecutor to parallelize the conversion process
    with ThreadPoolExecutor() as executor:
        # Map the conversion function to each PNG file
        futures = []
        for filename in png_files:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
            futures.append(executor.submit(convert_png_to_jpg, input_path, output_path))

        # Wait for all threads to complete
        for future in futures:
            future.result()


if __name__ == "__main__":
    input_folder = "rgb"
    output_folder = "rgb_jpg"

    convert_all_png_to_jpg(input_folder, output_folder)