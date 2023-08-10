# rgb labels to grey
python ~/fast_crop/blender_labels_to_dataset.py .
# remove any renders which failed
python ~/fast_crop/blender_complete_renders.py . really
# do histogram matching on rgb + exposed images
python ~/fast_crop/match_histograms.py rgb /ibex/user/kellyt/winlab_1/rgb rgb_histomatched
python ~/fast_crop/match_histograms.py exposed /ibex/user/kellyt/winlab_1/rgb exposed_histomatched

# create split files
cd rgb
ls -1 | sed -e 's/\.png$//' > ../all.txt
cd ..
cat all.txt | shuf > all_shuf.txt
cat all_shuf.txt | head -n 1024 > 1024.txt
# head -n 10000 all_shuf.txt > ptrain.txt
# tail -n 2000 all_shuf.txt > pval.txt

# build parameters for efficientNet
python ~/efficient/blender_process_attribs.py .

# create image-grids for professors
python ~/fast_crop/tmp_names_to_grid.py . "1024.txt" "labels" "png"
python ~/fast_crop/tmp_names_to_grid.py . "1024.txt" "exposed" "png"
python ~/fast_crop/tmp_names_to_grid.py . "1024.txt" "rgb" "png"

# print std and mean for synthetic photos to terminal (you'll want to save these for training)
python ~/fast_crop/find_mean_std.py "exposed" 1024
