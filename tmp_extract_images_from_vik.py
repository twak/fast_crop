import argparse
import json
import os


# script labellers used for counting results; fixed up by tom for technical details in email.

def get_json_file_paths(input_path):
    if not os.path.exists(input_path):
        raise ValueError(f"Path does not exist: '{input_path}'")

    if os.path.isfile(input_path):
        return [input_path]

    if os.path.isdir(input_path):
        return [
            os.path.join(input_path, filename)
            for filename in os.listdir(input_path)
        ]

    raise ValueError(f"Unsupported entity: '{input_path}'")


def extract_image_filenames(json_file_path):
    try:
        with open(json_file_path) as f:
            content = json.load(f)

        return [

            # tom's new code: files in the image section with corresponding entry in annotations section
            image['file_name'] for image in content['images'] if image["id"] in {poly["image_id"] for poly in content["annotations"]}

            #old code - only files in the image section
            #image['file_name'] for image in content['images']
        ]
    except Exception as e:
        print("Exception while reading file:", json_file_path)
        print(e)
        raise


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input_path',
        help='Path to input JSON file or directory with JSON files'
    )

    return parser.parse_args()


def main():
    args = get_args()

    image_files = { # tom changed this from a list to a set to only count unique names
        image_file
        for batch in os.listdir(args.input_path) # loop over all batches in the LYD__KAUST_all_batches.zip
            for json_file in get_json_file_paths(os.path.join ( args.input_path, batch ) )
                if json_file.endswith('.json')
                    for image_file in extract_image_filenames(json_file)
    }

    print(f"Images ({len(image_files)} total):")
    print()

    for image_file in image_files:
        print(image_file)

    print()
    print(f"Total: {len(image_files)}")


if __name__ == '__main__':
    main()
