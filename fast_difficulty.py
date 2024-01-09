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

import fast_crop_tags
import fast_crop_tags as tags
import pickle

import process_labels
import numpy as np

class ROI:

    def __init__(self, dir ):

        self.current_n = 0
        self.images = []
        abs_path = Path(dir).absolute()
        self.meta_dir = "/home/twak/Downloads/winlab_5/metadata_difficulty"
        os.makedirs(self.meta_dir, exist_ok=True)

        for exn in ("**.JPG", "**.jpg" ):
            self.images.extend(glob.glob(f"/home/twak/Downloads/winlab_5/rgb/*{exn}"))

        self.images.sort()

        # made with tmp_create_crop_lookup
        with open("/home/twak/Downloads/winlab_5/crop2path.pkl", "rb") as fp:
            self.crop2path = pickle.load(fp)

        if (len(self.images) == 0):
            print ("no images found in %s!" % dir)
            sys.exit(1)

        for i, f in enumerate (self.images): #  jump to last labelled
            if not os.path.exists(self.json_file(f)):
                self.current_n = i # skip to last annotated
                break

        print ("found %d images; starting at number %d" % (len (self.images), self.current_n ))

        self.photo_tags = {}
        self._pool = concurrent.futures.ThreadPoolExecutor()

        self.rect_tags = {}
        # self.photo_tags[ pygame.K_0 ] = ( tags.deleted, "0: Deleted")  # soft-delete: whole image not processed to dataset
        self.rect_tags[pygame.K_q] = ( tags.easy   , "q: Easy" )
        self.rect_tags[pygame.K_w] = ( tags.medium , "w: Medium" )
        self.rect_tags[pygame.K_e] = ( tags.hard   , "e: Hard")
        self.rect_tags[pygame.K_b] = ( tags.bad    , "b: Bad labels")

        self.default_tags   = [tags.easy]
        self.exclusive_tags = [tags.easy, tags.medium, tags.hard]

    def displayImage(self):

        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()) )

        self.screen.blit(self.px, (0,0))
        self.screen.blit( pygame.transform.scale(self.px, (1024,1024)), (0,0))
        self.screen.blit( pygame.transform.scale(self.pxLab, (1024,1024)), (1024,0))

        o = 0

        pygame.draw.rect(self.screen, (30, 30, 30), pygame.Rect(1000 + 0, 0, 160, len(self.tags) * 32 + 3))

        for t in self.tags:
            surface = self.font.render(t, True, (255, 255, 255) )
            self.screen.blit(surface, (1000 + 4, o * 32 + 6))
            o += 1

        pygame.display.flip()

    def mainLoop(self):
        self.topleft = self.bottomright = None

        while True:
            for event in pygame.event.get():

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_LEFT:
                        self.save()
                        self.load(-1)

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                        self.save()
                        self.load(+1)

                    for key, tag_desc in self.rect_tags.items():
                        if event.key == key:
                            tag = tag_desc[0]

                            if tag in self.exclusive_tags:
                                for e in self.exclusive_tags:
                                    if e in self.tags:
                                        self.tags.remove(e)

                            if tag in self.tags:
                                self.tags.remove(tag)
                            else:
                                self.tags.append (tag)

            self.displayImage()

    def pilImageToSurface(pilImage): #https://stackoverflow.com/a/64182629/708802
        return pygame.image.fromstring(
            pilImage.tobytes(), pilImage.size, pilImage.mode).convert()


    def json_file(self, pth = None):
        if pth == None:
            pth = self.input_loc

        root = Path(pth).with_suffix("").name

        for rr in [root, f"{root}.jpg", f"{root}.JPG"]:
            if rr in self.crop2path:
                c2p = Path(self.crop2path[rr])
                break

        return os.path.join (self.meta_dir, c2p.parent, f"{c2p.name}.json" )

    def photo2label(self, photo):
        pp = Path(photo)
        return pp.parent.joinpath("labels").joinpath(pp.with_suffix("jpg"))

    def save(self):

        json_file = self.json_file()
        os.makedirs(Path(json_file).parent, exist_ok=True)
        with open(json_file, "w") as file:
            json.dump(self.tags, file)
            print("saving %s" % file.name)

    @lru_cache(maxsize=8)
    def load_maybe_cache(self, file):
        im = Image.open(file)

        pf = Path(file)
        lab = np.array ( Image.open(pf.parent.parent.joinpath("labels").joinpath(pf.with_suffix(".png").name)) )

        pl_labels = process_labels.colours_for_mode(process_labels.PRETTY_NO_DOOR)
        color_seg = np.zeros((512,512, 3), dtype=np.uint8)
        totals = [0] * len (pl_labels)


        for label, color in enumerate(process_labels.LABEL_SEQ_NO_DOOR):
            lel = lab == label
            color_seg[lel, :] = pl_labels[color]
            totals[label] = lel.sum()

        trivial = [0, 5, 4, 2, 1]
        out_totals, out_count = 0, 0

        for i in range (len(totals)):
            if i not in trivial:
                out_totals += totals[i]
                out_count += 1 if totals[i] > 0 else 0

        lab = Image.fromarray(np.uint8(color_seg))
        f12s = 512*512


        if out_count <= 1 and (out_count == 0 or totals[10] > 0 or totals[3] > 0) and out_totals < f12s * 0.2: # if other/open/misc is misc/unlabelled then easy
            guess = fast_crop_tags.easy
        elif out_count >= 4:
            guess = fast_crop_tags.hard
        else:
            guess = fast_crop_tags.medium

        # print (f" out count {out_count}   out_totals {out_totals } = {guess}")

        return im, lab, guess

    def pre_load_image(self, file):
        self._pool.submit(self.load_maybe_cache, file)


    def load(self, incr):

        found_easy = False
        while not found_easy:
            self.rects = []
            self.current_rect = None

            self.tags = []
            self.current_n = (self.current_n + incr + len (self.images)) % len (self.images)

            self.input_loc = self.images[(self.current_n + len(self.images) ) % len(self.images)]
            print (f"loading {self.input_loc} ({self.current_n}/{len(self.images)})")
            pygame.display.set_caption(f"{self.input_loc} ({self.current_n}/{len(self.images)})")

            json_file = self.json_file()


            if os.path.exists(self.input_loc):
                self.im, self.lab, guess = self.load_maybe_cache(self.input_loc)
                if os.path.exists(json_file):
                    self.tags = json.load(open(json_file, "r"))

                    found_easy = fast_crop_tags.easy in self.tags

                else:
                    self.tags = [guess]
            else:
                self.tags = self.default_tags.copy()
                self.im, self.lab = Image.new("RGB", (10,10)),  Image.new("RGB", (10,10))
                self.tags = self.default_tags

            self.px    = ROI.pilImageToSurface(self.im)
            self.pxLab = ROI.pilImageToSurface(self.lab)

            # self.scale = max ( self.px.get_width()/self.screen.get_width(), self.px.get_height()/self.screen.get_height() )

            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()))
            pygame.display.flip()

            for i in range (1,3): # pre-cache following images
                self.pre_load_image( self.images[(self.current_n + i + len(self.images)) % len(self.images)] )

            if incr == 0:
                found_easy = True


    def interactive(self):

        pygame.init()

        pygame.font.init()

        self.font = pygame.font.SysFont('unispacebold', 48)
        if self.font is None:
            self.font = pygame.font.SysFont(pygame.font.get_default_font(), 10)

        self.screen = pygame.display.set_mode((2048, 1024))
        self.load(0)
        self.mainLoop()


def add_lookup(label_json_file, lookup):
    jp = Path(label_json_file)

    if os.stat(label_json_file).st_size == 0:  # while the labelling is in progress, some label files are empty placeholders.
        print(f"skipping empty label file {label_json_file}")
        return

    with open(label_json_file, "r") as f:
        data = json.load(f)

    c = 0
    for crop_name, crop_data in data.items():
        print(f"           {crop_name}")
        crop_name = crop_name.replace(".jpg", "")
        lookup[crop_name] = os.path.join(jp.parent.name, jp.name[:-5])
        c += 1

    return c


def build_lookup():
    json_src = []
    json_src.extend(glob.glob(r'./metadata_window_labels/*/*.json'))
    json_src.extend(glob.glob(r'./metadata_window_labels_2/*/*.json'))

    dataset_root = "."

    lookup = {}
    count = 0

    for j in json_src:
        print(j)
        count += add_lookup(j, lookup)

    print(f"found {count}")

    with open('/home/twak/Downloads/crop2path2.pkl', 'wb') as fp:
        pickle.dump(lookup, fp)


if __name__ == "__main__":

    # build_lookup()

    print("\n\n") #pygame output...

    if len ( sys.argv) == 1:
        path = "."
        print("first command line argument specifies the dataset root.\n")
    else:
        path = sys.argv[1]

    if len(sys.argv) < 3: # running interactive
        print("running interactive in %s." % path)
        ROI(path).interactive()
