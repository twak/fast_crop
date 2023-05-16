import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import lpips
import numpy as np
import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from pathlib import Path

from glob import glob

import os

loss_fn_alex = lpips.LPIPS(net='alex') # best forward scores
loss_fn_vgg = lpips.LPIPS(net='vgg') # closer to "traditional" perceptual loss, when used for optimization

img0 = torch.zeros(1,3,64,64) # image should be RGB, IMPORTANT: normalized to [-1,1]
img1 = torch.zeros(1,3,64,64)
d = loss_fn_alex(img0, img1)

loss_fn_alex.cuda()
loss_fn_vgg.cuda()

print(d)

class ImageFolder(Dataset):
    def __init__(self, root, transform=None):
        # self.fnames = list(map(lambda x: os.path.join(root, x), os.listdir(root)))
        self.fnames = glob(os.path.join(root, '**', '*.jpg'), recursive=True) + \
            glob(os.path.join(root, '**', '*.png'), recursive=True)

        self.transform = transform

    def __getitem__(self, index):
        image_path = self.fnames[index]
        image = Image.open(image_path).convert('RGB')
        if self.transform is not None:
            image = self.transform(image)
        return image

    def __len__(self):
        return len(self.fnames)

class SplitFile(Dataset):
    def __init__(self, txt, transform=None):

        self.fnames = []

        with open(txt) as f:
            for line in f:
                line = line.replace("\n", "")
                self.fnames.append( Path(txt).parent.joinpath("rgb").joinpath(f"{line}.png") )

        self.transform = transform

    def __getitem__(self, index):
        image_path = self.fnames[index]
        image = Image.open(image_path).convert('RGB')
        if self.transform is not None:
            image = self.transform(image)
        return image

    def __len__(self):
        return len(self.fnames)


class FileNames(Dataset):
    def __init__(self, fnames, transform=None):
        self.fnames = fnames
        self.transform = transform

    def __getitem__(self, index):
        image_path = self.fnames[index]
        image = Image.open(image_path).convert('RGB')
        if self.transform is not None:
            image = self.transform(image)
        return image

    def __len__(self):
        return len(self.fnames)


def get_custom_loader(image_dir_or_fnames, image_size=64, batch_size=1, num_workers=4, num_samples=-1):
    transform = []
    transform.append(transforms.Resize([image_size, image_size]))
    transform.append(transforms.ToTensor())
    transform.append(transforms.Normalize(mean=[0.5,0.5,0.5],
                                          std=[0.5,0.5,0.5]))
    transform = transforms.Compose(transform)

    if isinstance(image_dir_or_fnames, list):
        dataset = FileNames(image_dir_or_fnames, transform)
    elif isinstance(image_dir_or_fnames, str):
        if image_dir_or_fnames[-4:] == ".txt":
            dataset = SplitFile(image_dir_or_fnames, transform=transform)
        else:
            dataset = ImageFolder(image_dir_or_fnames, transform=transform)
    else:
        raise TypeError

    if num_samples > 0:
        dataset.fnames = dataset.fnames[:num_samples]
    data_loader = DataLoader(dataset=dataset,
                             batch_size=batch_size,
                             shuffle=False,
                             num_workers=num_workers,
                             pin_memory=True)
    return data_loader

if __name__ == '__main__':

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('path_real', type=str, help='Path to the real images')
    parser.add_argument('path_fake', type=str, help='Path to the fake images')
    args = parser.parse_args()

    results = []
    res = 256 # preview image size
    real_dataloader = get_custom_loader(args.path_real, batch_size=1)  # args.batch_size )
    fake_dataloader = get_custom_loader(args.path_fake, batch_size=1)  # args.batch_size )

    image_count = 4 # or zero to create splits

    layers=[0] # ?!

    if image_count > 0:
        image = np.zeros((image_count * res, (len(layers) + 1) * res, 3), dtype=np.uint8)
    else:
        split_fps = list(map(lambda layer: open(f"layer_2b_{layer}.txt", "w"), layers))

    for i, ti in enumerate(real_dataloader):
        # first_image = iter(dataloader).next()

        if image_count > 0 and i >= image_count:
            break  # done enough images

        # nearest fake index
        best_dist = 1e12
        for f, tf in enumerate(fake_dataloader):
            dist = loss_fn_alex.forward(ti.cuda(),tf.cuda())
            print(f"{i} -- {f} : {dist.flatten().tolist()[0]}")
            if dist < best_dist:
                best_dist = dist
                best_f = f

        # nearest = ipr.closest(ti, use_radii=False)
        # ipr.hide(nearest)  # use each image once-ish.

        if image_count > 0:  # add to image
            real_img = Image.open(real_dataloader.dataset.fnames[i])
            real_img.thumbnail((res, res), Image.Resampling.LANCZOS)
            image[i * res: (i + 1) * res, 0:res, 0:3] = np.asarray(real_img)

            fake_img = Image.open(fake_dataloader.dataset.fnames[best_f])
            fake_img.thumbnail((res, res), Image.Resampling.LANCZOS)
            image[i * res: (i + 1) * res, res * (0 + 1):res * (0 + 2), 0:3] = np.asarray(fake_img)[:, :, 0:3]
        else:  # add to split file
            split_fps[0].write(Path(fake_dataloader.dataset.fnames[best_f]).name[:-4] + "\n")

        # results.append((Path(fake_dataloader.dataset.fnames[i]).name[:-4], realism_score))

    if image_count > 0:
        print("writing image")
        Image.fromarray(image).save( f"/home/twak/Downloads/nearest_{datetime.time()}.jpg")
    else:
        for fo in split_fps:
            fo.close()