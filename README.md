# fast crop tool

Tom's collections of scrips for dataset wrangling the [WinSyn dataset](https://github.com/twak/winsyn_metadata). Code is still a bit rough, with hard coded pathes etc... Some scripts need to be run from the `root` or `data directories`. Pull requests welcome.

* [render_crops_and_labels.py](https://github.com/twak/fast_crop/blob/master/render_crops_and_labels.py) creates image + label datasets using the metadata_window_labels(_2) data.
* [render_crops.py](https://github.com/twak/fast_crop/blob/master/render_crops.py) creates cropped rgb images from the metadata_single_elements data.
* [build_website.py](https://github.com/twak/fast_crop/blob/master/build_website.py)
    * creates a website showing photos and crops by batches, and the photo locations. This is output to the metadata_website folder, which can be hosted by a webserver (e.g., Apache).
 (glass_facade, church, shop, abnormal, windows) might not be so reliable. The other classes (façade, material, private) are quite irregular.
    * the entire photo can also be annotated with 
        * _deleted - _the photo has been deleted from the dataset due to poor quality, containing no windows, or only containing windows repeated elsewhere in the batch
        * _rot90, rot180, rot270 _- the photo has been manually rotated before cropping (after any exif-encoded rotate has been applied).
* build_locations.py
    * creates the metadata_location folder containing different sources.
* [summary.py](https://github.com/twak/fast_crop/blob/master/figure_summary.py), 
    * outputs various statistics for the whole dataset.
* figure_many_xxx.py
    * scripts used to create the figures for the paper.
* [fast_crop.py](https://github.com/twak/fast_crop/blob/master/fast_crop.py)
    * the interactive tool used to create the metadata_single_elements folder. Allows windows (and other things) to be annotated. See below for details.
    * the _tags.py_ describes the different types of rectangular crops that may be annotated. Only the window classes are reliably applied. The window subclasses  (`glass_facade`, `church`, `shop`, `abnormal`, `window`) are all types of windows, but the division might not be so reliable. The other classes (façade, material, private) are quite irregular.
    * the entire photo can also be annotated with 
        * `deleted` - _the photo has been deleted from the dataset due to poor quality, containing no windows, or only containing windows repeated elsewhere in the batch
        * `rot90`, `rot180`, `rot270`- the photo has been manually rotated before cropping (after any exif-encoded rotate has been applied).
* build_locations.py
    * creates the metadata_location folder containing different sources. Currently in progress.
* [summary.py](https://github.com/twak/fast_crop/blob/master/figure_summary.py), 
    * outputs various statistics for the whole dataset.
* figure_xxx.py
    * scripts used to create the figures for the paper.


## [fast_crop](https://github.com/twak/fast_crop/blob/master/fast_crop.py)

This was the first tool in the repo and is what we used to mark window rectangles in many photos. You can also tag the rectangles with additional metadata. It was mainly engineered written to fast + hackable. 

```
python crop_tool.py "C:\Downloads\dataset\twak_london_20220522"
```

If the window is too big you can edit a line (about 286) `self.screen = pygame.display.set_mode((1600, 1600))` to change the resolution of the window to however big you want.

The interface is designed for throughput rather than comfort. The data is written when you advance to the next image, so if you make a mistake, close the program without advancing and start again!

keys:

* `left` (or `space`), `right` - advance through the images in the folder. if you do not draw a rectangle, it will mark the whole photo as a window. To not include any rectangles, press `0` to soft-delete the photo.
* `r` rotate the image
* mouse - draw rectangle. all new rectangles are currently given the `window` tag or the tags from the current rectangle.
* `F1` - show rectangle-class cheat sheet
* pink letters at top left: add/remove tags to the current rectangle or entire image
* `up`, `down` - change the current rectangle
* `backspace` - remove current rectangle
* `c` - clear all rectangles from current photo.
* `0` - toggle soft delete/ignore (any marked rectangles will be ignored)
* `z` - cycle cursor modes (crosshairs/zoom) 
