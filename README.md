# fast crop tool

Tom's collections of scrips for dataset generation. 

## crop_tool

This is a custom tool to mark window rectangles in many photos quickly. You can also tag the rectangles with additional metadata. 

```
python crop_tool.py "C:\Downloads\dataset\twak_london_20220522"
```

If the window is too big you can edit a line (about 286) `self.screen = pygame.display.set_mode((1600, 1600))` to change the resolution of the window to however big you want.

The interface is designed for throughput rather than comfort. The data is written when you advance to the next image, so if you make a mistake, close the program without advancing and start again!

keys:

* `F1` - show rectangle-class cheat sheet
* `left` (or `space`), `right` - advance through the images in the folder. if you do not draw a rectangle, it will mark the whole photo as a window. To not include any rectangles, press `0` to ignore the photo entirely.
* mouse - draw rectangle. all new rectangles are currently given the `window` tag or the tags from the current rectangle.
* pink letters at top left: add/remove tags to the current rectangle or entire image
* `up`, `down` - change the current rectangle
* `backspace` - remove current rectangle
* `c` - remove all rectangles from current photo.
* `0` - toggle soft delete/ignore (any marked rectangles will be ignored)
* `z` - cycle cursor modes (crosshairs/zoom) 
