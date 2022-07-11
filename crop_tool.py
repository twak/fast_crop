import glob
import hashlib
import json
import os

import PIL.Image
import pygame, sys
from PIL import Image, ImageOps
from pathlib import Path
import tags

class ROI:

    def __init__(self, dir ):

        self.current_n = 0
        self.images = []
        self.meta_dir = Path(dir).parent.parent.joinpath("metadata_single_elements/%s" % os.path.basename(dir) )
        os.makedirs(self.meta_dir, exist_ok=True)

        for exn in ("**.jpg", "**.png" ):
            self.images.extend(glob.glob(dir+"/"+exn))

        if (len(self.images) == 0):
            print ("no images found in %s!" % dir)
            sys.exit(1)

        for i, f in enumerate (self.images):
            if os.path.exists(self.json_file(f)):
                self.current_n = i # skip to last annotated

        print ("found %d images; starting at number %d" % (len (self.images), self.current_n ))

        self.rect_tags = {}
        self.photo_tags = {}

        self.photo_tags[ pygame.K_0 ] = ( tags.deleted, "0: Deleted")  # whole image not processed to dataset

        self.rect_tags[pygame.K_1] = ( tags.glass_facade, "1: Glass Facade" ) # glass panels
        self.rect_tags[pygame.K_2] = ( tags.church      , "2: Church" )# complex church window
        self.rect_tags[pygame.K_3] = ( tags.shop        , "3: Shop")  # street level/wide angle shot
        self.rect_tags[pygame.K_4] = ( tags.abnormal    , "4: Abnormal")  # street level/wide angle shot
        self.rect_tags[pygame.K_5] = ( tags.door        , "5: Door")  # a door!
        self.rect_tags[pygame.K_6] = ( tags.facade      , "6: Facade")  # a large amount of a building
        self.rect_tags[pygame.K_w] = ( tags.window      , "w: Window")  # we are creating windows
        self.rect_tags[pygame.K_m] = ( tags.material    , "m: Material")  # we are marking materials

        self.default_tags = [tags.window]
        self.exclusive_tags = [tags.window, tags.material, tags.door, tags.facade] # pick one!

    def displayImage(self):

        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()) )

        rect = self.px.get_rect()

        px = pygame.transform.scale(self.px, [rect.width / self.scale, rect.height / self.scale])
        self.screen.blit(px, px.get_rect())

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

        # tags at top left
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

    def load(self, incr):

        self.rects = []
        self.current_rect = None

        self.tags = []
        self.current_n += incr

        self.input_loc = self.images[(self.current_n + len(self.images) ) % len(self.images)]
        print ("loading %s" % self.input_loc)
        pygame.display.set_caption(self.input_loc)

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
