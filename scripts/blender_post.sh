python ~/fast_crop/blender_labels_to_dataset.py .
python ~/fast_crop/blender_complete_renders.py . really
cd rgb
ls -1 | sed -e 's/\.png$//' > ../all.txt
cd ..
cat all.txt | shuf > all_shuf.txt
cat all_shuf.txt | head -n 1024 > 1024.txt
python ~/efficient/blender_process_attribs.py .
python ~/fast_crop/tmp_names_to_grid.py . "1024.txt" "exposed" "png"
python ~/fast_crop/find_mean_std.py "rgb" 1024
