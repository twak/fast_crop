import glob
import hashlib
import json
import os

import PIL.Image
import pygame, sys
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path

class ROI:

    def __init__(self, dir ):

        # load index from all image filenames
        # load rects

        self.current_n = 0
        self.images = []
        self.meta_dir = Path(dir).parent.joinpath("metadata_single_elements/%s" % os.path.basename(dir) )
        os.makedirs(self.meta_dir, exist_ok=True)

        for exn in ("**.jpg", "**.png" ):
            self.images.extend(glob.glob(dir+"/"+exn))

        if (len(self.images) == 0):
            print ("no images found in %s!" % dir)
            sys.exit(1)

        for i, f in enumerate (self.images):
            if os.path.exists(self.json_file(f)):
                self.current_n = i # skip to last annotated

        print ("found %d images" % len (self.images))

        self.keys = {}

        self.keys['deleted'] = "0: Deleted"  # whole image not processed to dataset
        self.keys['glass_facade'] = "1: Glass Facade" # glass panels
        self.keys['church'] = "2: Church" # complex church window
        self.keys['street'] = "3: Shop" # street level/wide angle shot

        self.keys['win'] = "w: Window"  # we are creating windows

    def displayImage(self):

        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()) )

        rect = self.px.get_rect()

        px = pygame.transform.scale(self.px, [rect.width / self.scale, rect.height / self.scale])
        self.screen.blit(px, px.get_rect())

        if self.rects is not None:
            for x, y, x2, y2 in self.rects:
                pygame.draw.rect(self.screen, (0, 200, 0), pygame.Rect( x / self.scale, y/ self.scale, (x2-x)/ self.scale, (y2-y)/ self.scale ), width = 1 )

        if 'deleted' in self.tags:
            pygame.draw.line(self.screen, (255, 0, 0), (0, 0), (self.screen.get_width(), self.screen.get_height()))
            pygame.draw.line(self.screen, (255, 0, 0), (self.screen.get_width(), 0), (0, self.screen.get_height()))

        # tags at top left
        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0,0, 120, len(self.keys) * 16 ))
        o = 0
        for t, d in self.keys.items():
            color = (255, 0, 255) if t in self.tags else (0, 255, 255)
            surface = self.font.render(d, True, color)
            self.screen.blit (surface, (5, o * 16) )
            o = o + 1

        if self.topleft is not None and self.bottomright is not None:
            x, y = self.topleft
            width =  self.bottomright[0] - self.topleft[0]
            height = self.bottomright[1] - self.topleft[1]
            if width < 0:
                x += width
                width = abs(width)
            if height < 0:
                y += height
                height = abs(height)

            pygame.draw.line(self.screen, (255, 0, 255), (0, y), (self.screen.get_width(), y))
            pygame.draw.line(self.screen, (255, 0, 255), (0, y + height), (self.screen.get_width(), y + height))
            pygame.draw.line(self.screen, (255, 0, 255), (x, 0), (x, self.screen.get_height()))
            pygame.draw.line(self.screen, (255, 0, 255), (x + width, 0), (x + width, self.screen.get_height()))
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect( x, y, width, height ), width = 1 )

        pygame.display.flip()

    def mainLoop(self):
        self.topleft = self.bottomright = None

        while True:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                        self.topleft = list(event.pos)
                if event.type == pygame.MOUSEMOTION:
                        self.bottomright = list(event.pos)
                if event.type == pygame.MOUSEBUTTONUP:

                        if self.topleft is None or self.bottomright is None: # mouse scroll
                            continue

                        if self.topleft[0] > self.bottomright[0]:
                            tmp = self.topleft[0]
                            self.topleft[0] = self.bottomright[0]
                            self.bottomright[0] = tmp

                        if self.topleft[1] > self.bottomright[1]:
                            tmp = self.topleft[1]
                            self.topleft[1] = self.bottomright[1]
                            self.bottomright[1] = tmp

                        r = [self.topleft[0] * self.scale, self.topleft[1] * self.scale, self.bottomright [0] * self.scale, self.bottomright [1] * self.scale]
                        # clamp r
                        r[0] = min(max(0, r[0]), self.im.width)
                        r[1] = min(max(0, r[1]), self.im.height)
                        r[2] = min(max(0, r[2]), self.im.width)
                        r[3] = min(max(0, r[3]), self.im.height)

                        if self.rects is None:
                            self.rects = []
                        self.rects.append(r)

                        self.topleft = self.bottomright = None


                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        self.save()
                        self.load(-1)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                        self.save()
                        self.load(+1)

                    if event.key == pygame.K_c:
                        self.rects = []


                    if event.key == pygame.K_BACKSPACE:
                        if len (self.rects) > 0:
                            self.rects = self.rects[:-1]

                    if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                        ind = event.key - pygame.K_0
                        if ind < len (self.keys):
                            val = list(self.keys.keys())[ind]
                            if val in self.tags:
                                self.tags.remove(val)
                            else:
                                self.tags.append (val)


                if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or event.type == pygame.QUIT:
                        self.save()
                        pygame.display.quit()
                        sys.exit(0)

            self.displayImage()

    def pilImageToSurface(pilImage): #https://stackoverflow.com/a/64182629/708802
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert()



    def json_file(self, pth = None):
        if pth == None:
            pth = self.input_loc;

        pre, ext = os.path.splitext(pth)

        return  os.path.join(self.meta_dir, os.path.basename(pre)+".json")


    def save(self):

        if (self.rects is None or len (self.rects) == 0) and len(self.tags) == 0:
            print ("not saving (no rects) %s" % self.input_loc)
            return

        out = {"rects": self.rects, "width": self.im.width, "height": self.im.height, "tags": self.tags}

        with open(self.json_file(), "w") as file:
            json.dump(out, file)
            print("saving %s" % file.name)

    def load(self, incr):

        self.rects = []
        self.tags = []
        self.current_n += incr

        self.input_loc = self.images[(self.current_n + len(self.images) ) % len(self.images)]
        print ("loading %s" % self.input_loc)
        pygame.display.set_caption(self.input_loc)

        json_file = self.json_file()
        if os.path.exists(json_file):
            prev = json.load(open(json_file, "r"))
            self.rects = prev["rects"]
            if "tags" in prev:
                self.tags = prev["tags"]


        if os.path.exists(self.input_loc):
            im = Image.open(self.input_loc)
            self.im = im = ImageOps.exif_transpose(im)
        else:
            self.rects = None
            self.im = Image.new("RGB", (10,10))
            print("error: file once seen is now missing :(")

        self.px = ROI.pilImageToSurface(im)
        self.scale = max ( self.px.get_width()/self.screen.get_width(), self.px.get_height()/self.screen.get_height() )

        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()))

        pygame.display.flip()

    def interactive(self):

        pygame.init()

        pygame.font.init()

        self.font = pygame.font.SysFont('unispacebold', 10)
        if self.font is None:
            self.font = pygame.font.SysFont(pygame.font.get_default_font(), 10)

        self.screen = pygame.display.set_mode((1600, 1600))
        self.load(0)
        self.mainLoop()


    def crop(self, img, res = -1, mode = 'none'):


        if mode == 'none':
            return img

        if mode == 'square_crop': # https://stackoverflow.com/questions/16646183/crop-an-image-in-the-centre-using-pil

            width  = img.size[0]
            height = img.size[1]

            new_width = min(width, height)

            left = int(np.ceil((width - new_width) / 2))
            right = width - np.floor((width - new_width) / 2)

            top = int(np.ceil((height - new_width) / 2))
            bottom = height - int(np.floor((height - new_width) / 2))

            img = img.crop ((left, top, right, bottom))

            if res != -1:
               img =  img.resize( (res, res), resample = PIL.Image.Resampling.BOX)

            return img

        if mode == 'square_expand':

            width  = img.size[1]
            height = img.size[0]

            wh  = min(width, height)
            img = ImageOps.pad(img, (wh, wh), color="black")

            if res != -1:
               img =  img.resize( (res, res), resample = PIL.Image.Resampling.BOX)

            return img

    # def move_tag(self, tag_to_move, destination):
    #
    #     for im_file in self.images:
    #         json_file = self.json_file(im_file)
    #
    #         base_dir = os.path.basename(im_file)
    #
    #         if os.path.exists(json_file): # crop
    #             prev = json.load(open(json_file, "r"))
    #             tags = prev["tags"]
    #             if tag_to_move in tags:
    #                 # print(json_file)
    #                 # print(im_file)
    #                 # print("\n")
    #                 os.rename(json_file, os.path.join(destination, os.path.basename(json_file)))
    #                 os.rename(im_file  , os.path.join(destination, os.path.basename(  im_file)))


    def cut_n_shut(self, dir_, clear_log = False, sub_dirs = True, crop_mode='square_crop', resolution = 512):

        global VALID_CROPS

        os.makedirs(dir_, exist_ok=True)
        dir = dir_

        fm = 'w' if clear_log else 'a'
        log = open( os.path.join ( dir_, 'log.txt'), fm)

        def save(im, out_name, count):

            if len (im.getbands() ) > 3: # pngs..
                 im = im.convert("RGB")

            if im.width == 0 or im.height == 0:
                print("skipping zero sized rect in %s" % out_name)
                return

            md5hash = hashlib.md5(im.tobytes())
            jpg_out_file = "%s.jpg" % md5hash.hexdigest()
            log.write("\"%s\"\n" % jpg_out_file)


            out_path = os.path.join(dir, jpg_out_file)

            im.save(out_path, format="JPEG", quality=98)

        if not crop_mode in VALID_CROPS:
            print ("unknown crop mode %s. pick from: %s " % (crop_mode, " ".join(VALID_CROPS)))
            return

        # resolution = 512
#        mode = 'square_crop'
#         crop_mode = 'square_expand'
#         crop_mode = 'none'
        min_dim = 2048 # 1024 lost 77/3,100 at this resolution (12.4.22)

        for im_file in self.images:

            if sub_dirs:
                sub_dir = os.path.split ( os.path.split(im_file)[0] )[1]
                dir = os.path.join(dir_, sub_dir)
                os.makedirs( dir, exist_ok=True)

            print ('processing %s...' % im_file)

            im = ImageOps.exif_transpose(Image.open(im_file))

            out_name, out_ext = os.path.splitext ( os.path.basename(im_file) )
            out_ext = out_ext.lower()

            pre, ext = os.path.splitext(im_file)
            json_file = pre + ".json"

            count = 0

            if os.path.exists(json_file): # crop
                prev = json.load(open(json_file, "r"))
                rects = prev["rects"]

                tags = []

                if "tags" in prev:
                    tags = prev["tags"]

                if 'deleted' in tags:
                    print("skipping deleted")
                    continue

                for r in rects:

                    if r[2] - r[0] < min_dim or r[3] - r[1] < min_dim:
                        print("skipping small rect")
                        continue

                    log.write("%s [%d, %d, %d, %d]\n" % (im_file, r[0], r[1], r[2], r[3]) )

                    crop_im = im.crop( ( r[0], r[1], r[2], r[3] ) )
                    crop_im = self.crop(crop_im, resolution, crop_mode)

                    save(crop_im, out_name, count)
                    count = count + 1
            else: # whole image
                im = self.crop(im, resolution, crop_mode)
                log.write(im_file + f"[0,0,{im.width},{im.height}]\n")
                save ( im, out_name, count )

        log.close()


VALID_CROPS = {'square_crop', 'square_expand', 'none'}

if __name__ == "__main__":

    print("\n\n") #pygame output...

    if len ( sys.argv) == 1:
        path = "."
        print("the first command line argument specifies the folder location - using python root for now. Other instructions: \n")
        print("second argument is the output folder - this switches us to image processing mode (crops and writes images to output)")
        print("third argument is the optional crop mode: %s " % ", ".join(VALID_CROPS))
        print("fourth argument is the optional resolution (used if crop_mode is not 'none')")
    else:
        path = sys.argv[1]

    if len(sys.argv) < 3: # running interactive
        print("running interactive in %s." % path)
        ROI(path).interactive()

    else: # process output
        out = sys.argv[2]
        print("cropping images from %s to %s" % (path, out) )
        crop_mode = 'none'
        resolution = 512
        if len(sys.argv) >= 4:
            crop_mode = sys.argv[3]
        if len(sys.argv) >= 5:
            resolution = int ( sys.argv[4] )

        ROI( path ).cut_n_shut(out, clear_log=True, crop_mode = crop_mode, resolution = resolution)

    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_dales').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_bramley').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_archive').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_leeds_docks').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_york').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_saffron').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_cams').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_london').interactive()
    #ROI('C:/Users/twak/Documents/architecture_net/windowz_images/Michaela_Windows_Vienna_20220505').interactive()
    # ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_london').move_tag('deleted', 'C:\\Users\\twak\Documents\\architecture_net\\not_windowz' )

    if False: # generate whole dataset on tom's machine
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_york').cut_n_shut(out, clear_log= True)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_leeds_docks').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_bramley').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_dales').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_saffron').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_cams').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_london').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_archive').cut_n_shut(out)
        ROI('C:/Users/twak/Documents/architecture_net/windowz_images/Michaela_Windows_Vienna_20220505').cut_n_shut(out)
