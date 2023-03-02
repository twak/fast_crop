import os
from pathlib import Path

dataset_root = "."

for batch in os.listdir(os.path.join(dataset_root, "photos")):
    if "michaela_vienna" in batch and not ( "20220427" in batch or "20220428" in batch):
        print(" >>>>>>>>>>> "+ batch)
        label_dir = os.path.join(dataset_root, "metadata_window_labels",  batch)



        if os.path.exists(label_dir):
            for json in os.listdir(label_dir):
                if json.endswith(".json"):
                    json_file = os.path.join(label_dir, json)

                    n = 1

                    new_name = f"{json[0:4]}-0{n}{json[4:]}" # _NZ70689.json -> _NZ7-010689.json


                    print (f"renaming {json} to {new_name} ")

                    if not Path(dataset_root).joinpath("photos", batch).joinpath(Path(new_name).with_suffix(".JPG")).exists():
                        print("but missing photo file!")
                        continue

                    # os.rename(json_file, os.path.join(label_dir, new_name) )


