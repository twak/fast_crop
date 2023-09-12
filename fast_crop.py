import concurrent
import concurrent.futures
import glob
import hashlib
import json
import os
from functools import lru_cache

import PIL.Image
import pygame, sys
from PIL import Image, ImageOps
from PIL.Image import Transpose
from pathlib import Path
import fast_crop_tags as tags

ROTS = ["rot90", "rot180", "rot270"]

class ROI:

    def __init__(self, dir ):

        self.current_n = 0
        self.images = []
        abs_path = Path(dir).absolute()
        self.meta_dir = abs_path.parent.parent.joinpath("metadata_single_elements").joinpath(abs_path.name).joinpath(os.path.basename(dir) )
        os.makedirs(self.meta_dir, exist_ok=True)

        for exn in ("**.JPG", "**.jpg" ):
            self.images.extend(glob.glob(dir+"/"+exn))

        self.images.sort()

        if (len(self.images) == 0):
            print ("no images found in %s!" % dir)
            sys.exit(1)

        for i, f in enumerate (self.images):
            if not os.path.exists(self.json_file(f)):
                self.current_n = i # skip to last annotated
                break

        print ("found %d images; starting at number %d" % (len (self.images), self.current_n ))

        self.rect_tags = {}
        self.photo_tags = {}
        self.cursor_widgets = 0
        self.show_help = False
        self._pool = concurrent.futures.ThreadPoolExecutor()

        self.photo_tags[ pygame.K_0 ] = ( tags.deleted, "0: Deleted")  # soft-delete: whole image not processed to dataset

        self.rect_tags[pygame.K_g] = ( tags.glass_facade, "g: Glass Facade Window" )
        self.rect_tags[pygame.K_h] = ( tags.church      , "h: Church Window" )
        self.rect_tags[pygame.K_s] = ( tags.shop        , "s: Shop Window")
        self.rect_tags[pygame.K_z] = ( tags.abnormal    , "z: Abnormal Window")
        self.rect_tags[pygame.K_d] = ( tags.door        , "d: Door")
        self.rect_tags[pygame.K_f] = ( tags.facade      , "f: Facade")
        self.rect_tags[pygame.K_w] = ( tags.window      , "w: Window (regular!)")
        self.rect_tags[pygame.K_m] = ( tags.material    , "m: Material")
        self.rect_tags[pygame.K_p] = ( tags.private     , "p: Private")

        self.default_tags   = [tags.window]
        self.exclusive_tags = [tags.window, tags.material, tags.door, tags.facade, tags.private] # picking one removes others

    def displayImage(self):

        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()) )

        rect = self.px.get_rect()

        px = pygame.transform.scale(self.px, [rect.width / self.scale, rect.height / self.scale])
        self.screen.blit(px, px.get_rect())

        if self.bottomright is not None and self.topleft is None and self.cursor_widgets < 2:
            size = 64
            cropped = pygame.Surface((size*2, size*2))
            cropped.blit(self.px, [-self.bottomright[0] * self.scale+size, -self.bottomright[1] * self.scale+size] )
            self.screen.blit(cropped, [self.bottomright[0]-size, self.bottomright[1]-size])
            # self.screen.blit(px, px.get_rect())

        if self.rects is not None:
            for rect in self.rects:
                x, y, x2, y2 = rect[0]

                color = (255, 255, 255) if rect == self.current_rect else (200, 200, 200)
                width = 3 if rect == self.current_rect else 1

                pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(x / self.scale, y / self.scale, (x2 - x) / self.scale, (y2 - y) / self.scale), width=2*width)

                # tags
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(x / self.scale, y / self.scale, 16, len(rect[1]) * 16))
                o = 0
                for t in rect[1]:
                    # color = (255, 0, 255) if t in self.tags else (0, 255, 255)
                    surface = self.font.render(t[0], True, color)
                    self.screen.blit(surface, (x / self.scale + 4, y / self.scale + o * 16 + 3))
                    o += 1

                # rect border
                pygame.draw.rect(self.screen, color, pygame.Rect(x / self.scale, y / self.scale, (x2 - x) / self.scale, (y2 - y) / self.scale), width=width)

        if 'deleted' in self.tags:
            pygame.draw.line(self.screen, (255, 0, 0), (0, 0), (self.screen.get_width(), self.screen.get_height()), width = 10)
            pygame.draw.line(self.screen, (255, 0, 0), (self.screen.get_width(), 0), (0, self.screen.get_height()), width = 10)

        # tag-list at top left
        if self.show_help:
            all_tags = self.photo_tags.items() | self.rect_tags.items()
            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(self.screen.get_width() -120, 0,120, len(all_tags) * 16 ))
            o = 0
            for t, d in all_tags:
                # color = (255, 0, 255) if t in self.current_rect[1] else (0, 255, 255)
                color = (255, 0, 255)
                surface = self.font.render(d[1], True, color)
                self.screen.blit (surface, (self.screen.get_width()-120+5, o * 16) )
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

            pygame.draw.line(self.screen, (255, 0  , 255), (0, y), (self.screen.get_width(), y))
            pygame.draw.line(self.screen, (255, 0  , 255), (0, y + height), (self.screen.get_width(), y + height))
            pygame.draw.line(self.screen, (255, 0  , 255), (x, 0), (x, self.screen.get_height()))
            pygame.draw.line(self.screen, (255, 0  , 255), (x + width, 0), (x + width, self.screen.get_height()))
            pygame.draw.rect(self.screen, (0  , 255, 0  ), pygame.Rect( x, y, width, height ), width = 1 )
        elif self.bottomright is not None and self.cursor_widgets % 2 == 0: # always show a garget
            x, y = self.bottomright
            pygame.draw.line(self.screen, (255, 0, 255), (0, y), (self.screen.get_width(), y))
            pygame.draw.line(self.screen, (255, 0, 255), (x, 0), (x, self.screen.get_height()))

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

                        template_tags = self.default_tags if self.current_rect is None else self.current_rect[1]
                        self.current_rect = (r, template_tags.copy())
                        self.rects.append(self.current_rect)

                        self.topleft = self.bottomright = None


                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        self.save()
                        self.load(-1)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                        self.save()
                        self.load(+1)

                    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        if self.current_rect != None and self.current_rect in self.rects:
                            i = self.rects.index(self.current_rect)
                            dir = 1 if event.key == pygame.K_DOWN else -1
                            self.current_rect = self.rects[(i+len ( self.rects ) + dir)%len ( self.rects )]

                    if event.key == pygame.K_c:
                        self.rects = []
                        self.current_rect = None

                    if event.key == pygame.K_a:
                        self.current_rect = ([0,0,self.im.width,self.im.height], self.default_tags.copy())
                        self.rects.append(self.current_rect)

                    if event.key == pygame.K_BACKSPACE:
                        if self.current_rect in self.rects:
                            i = self.rects.index(self.current_rect)
                            self.rects.remove(self.current_rect)
                            if len(self.rects) > 0:
                                self.current_rect = self.rects[(i % len ( self.rects ))]
                            else:
                                self.current_rect = None

                    if event.key == pygame.K_z:
                        self.cursor_widgets = ( self.cursor_widgets + 1 ) % 4

                    if event.key == pygame.K_F1:
                        self.show_help ^= True

                    if event.key == pygame.K_r:
                        self.incRot(1)
                        self.rects = []
                        self.current_rect = None
                        self.im = self.im.transpose(Transpose.ROTATE_90)
                        self.px = ROI.pilImageToSurface(self.im)

                    if self.current_rect != None:
                        for key, tag_desc in self.rect_tags.items():
                            if event.key == key:

                                tag = tag_desc[0]



                                if tag in self.current_rect[1]:
                                    self.current_rect[1].remove(tag)
                                else:
                                    if tag in self.exclusive_tags:
                                        for t2 in self.exclusive_tags:
                                            if t2 in self.current_rect[1]:
                                                self.current_rect[1].remove(t2)

                                    self.current_rect[1].append(tag)

                    for key, tag_desc in self.photo_tags.items():
                        if event.key == key:
                            tag = tag_desc[0]
                            if tag in self.tags:
                                self.tags.remove(tag)
                            else:
                                self.tags.append (tag)

                if (event.type == pygame.KEYDOWN and event.key == pygame.K_q) or event.type == pygame.QUIT:
                        self.save()
                        pygame.display.quit()
                        sys.exit(0)

            self.displayImage()

    def incRot(self, i):
        # angle is exif rotation + 90 * rot (counter clockwise)
        global ROTS

        rot = (self.getRot() + i) % 4

        for r in ROTS:
            if r in self.tags:
                self.tags.remove (r)

        if rot != 0:
            self.tags.append(ROTS[rot-1])

        print(f"incRot {rot}")

        return rot

    def getRot(self):

        # angle is exif rotation + 90 * this (counter clockwise)
        for i, r in enumerate(ROTS):
            if r in self.tags:
                return i + 1

        return 0

    def pilImageToSurface(pilImage): #https://stackoverflow.com/a/64182629/708802
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert()



    def json_file(self, pth = None):
        if pth == None:
            pth = self.input_loc

        pre, ext = os.path.splitext(pth)

        return  os.path.join(self.meta_dir, os.path.basename(pre)+".json")


    def save(self):

        # if (self.rects is None or len (self.rects) == 0) and len(self.tags) == 0 and not os.path.exists(self.json_file()):
        #     print ("not saving (no rects) %s" % self.input_loc)
        #     return

        if len ( self.rects ) == 0 and 'deleted' not in self.tags:
            self.rects.append( [[0,0,self.im.width, self.im.height], self.default_tags.copy()] )

        out = {"rects": self.rects, "width": self.im.width, "height": self.im.height, "tags": self.tags}

        with open(self.json_file(), "w") as file:
            json.dump(out, file)
            print("saving %s" % file.name)

    @lru_cache(maxsize=8)
    def load_maybe_cache(self, file):
        im = Image.open(file)
        return ImageOps.exif_transpose(im)

    def pre_load_image(self, file):
        self._pool.submit(self.load_maybe_cache, file)


    def load(self, incr):

        self.rects = []
        self.current_rect = None

        self.tags = []
        self.current_n = (self.current_n + incr + len (self.images)) % len (self.images)

        self.input_loc = self.images[(self.current_n + len(self.images) ) % len(self.images)]
        print (f"loading {self.input_loc} ({self.current_n}/{len(self.images)})")
        pygame.display.set_caption(f"{self.input_loc} ({self.current_n}/{len(self.images)})")

        json_file = self.json_file()
        if os.path.exists(json_file):
            prev = json.load(open(json_file, "r"))
            self.rects = prev["rects"]
            if len(self.rects) > 0:
                self.current_rect = self.rects[-1]
            else:
                self.current_rect = None

            if "tags" in prev:
                self.tags = prev["tags"]

        if os.path.exists(self.input_loc):
            self.im = self.load_maybe_cache(self.input_loc)
            rot = self.getRot()
            if rot > 0:
                self.im = self.im.transpose( [Transpose.ROTATE_90, Transpose.ROTATE_180, Transpose.ROTATE_270][rot-1] )
        else:
            self.rects = None
            self.im = Image.new("RGB", (10,10))
            print("error: file once seen is now missing :(")

        self.px = ROI.pilImageToSurface(self.im)
        self.scale = max ( self.px.get_width()/self.screen.get_width(), self.px.get_height()/self.screen.get_height() )

        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()))

        pygame.display.flip()

        for i in range (1,3): # pre-cache following images
            self.pre_load_image( self.images[(self.current_n + i + len(self.images)) % len(self.images)] )
        # print ( self.load_maybe_cache.cache_info() )

    def interactive(self):

        pygame.init()

        pygame.font.init()

        self.font = pygame.font.SysFont('unispacebold', 10)
        if self.font is None:
            self.font = pygame.font.SysFont(pygame.font.get_default_font(), 10)

        self.screen = pygame.display.set_mode((1600, 1600))
        self.load(0)
        self.mainLoop()

if __name__ == "__main__":

    print("\n\n") #pygame output...

    if len ( sys.argv) == 1:
        path = "."
        print("first command line argument specifies the dataset root.\n")
    else:
        path = sys.argv[1]

    if len(sys.argv) < 3: # running interactive
        print("running interactive in %s." % path)
        ROI(path).interactive()

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
    # if False: # generate whole dataset on tom's machine
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_york').cut_n_shut(out, clear_log= True)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_leeds_docks').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_bramley').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_dales').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_saffron').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_cams').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_london').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/tom_archive').cut_n_shut(out)
    #     ROI('C:/Users/twak/Documents/architecture_net/windowz_images/Michaela_Windows_Vienna_20220505').cut_n_shut(out)
