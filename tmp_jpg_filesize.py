import os
import fnmatch

def get_total_jpeg_size(root_directory):
    total_size = 0

    for root, _, files in os.walk(root_directory):
        for file in files:
            if fnmatch.fnmatch(file, '*.jpg') or fnmatch.fnmatch(file, '*.JPG'):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

    return total_size

# Replace 'your_directory_path' with the actual path to your directory
directory_path = '.'
total_jpeg_size = get_total_jpeg_size(directory_path)

print(f"Total JPEG file size: {total_jpeg_size} bytes")