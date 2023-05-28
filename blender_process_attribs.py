import os
import sys
from collections import defaultdict
from glob import glob
import json
from statistics import mean, stdev
from pathlib import Path

import numpy as np

PCOUNT = 1000
CONFIG_JSON = "param_config.json"

class Param():

    def __init__(self, name):
        self.name = name
        self.values = []

    def add(self, value):
        self.values.append(value)

    def is_continuous(self):
        # one or more non-integer value
        return any( map ( lambda v: False if isinstance(v, int) else not v.is_integer(), self.values) )

    def max(self):
        return max(self.values)

    def min(self):
        return min(self.values)

    def mean(self):
        return mean(self.values)

    def std(self):
        if len(self.values) > 2:
            return stdev(self.values)
        return 0

def attr_it(dataset):
    for f in glob(f"{dataset}/attribs/*.txt"):
        print (f)
        with open(f, 'r') as fp:
            txt = fp.read().split("\n")
            txt[-3] = txt[-3].replace(",", "") # extra comma on final attribute

            f_params = json.loads("".join(txt))

            yield f_params, Path(f).name


def build_config(dataset):
    params = {} # defaultdict(lambda x: Param(x))

    for f_params, _ in attr_it(dataset):
            for k, v in f_params.items():
                if k not in params:
                    params[k] = Param(k)
                params[k].add(v)

    print(f"found {len(params)} values")

    l = list ( params.values() )
    l.sort ( key = lambda p : -len ( p.values) )

    cont = []
    disc = []
    global PCOUNT
    d_sofar = 0

    for p in l:

        std = p.std()

        if std == 0: # ?!
            continue

        p_summary = dict(name=p.name, min = p.min(), max=p.max(), mean=p.mean(), std=std)

        if p.is_continuous():
            if len(cont) < PCOUNT:
                cont.append(p_summary)
        else:
            maax, miin = p.max(), p.min()
            d_size = maax - miin + 1
            if d_sofar + d_size < PCOUNT and d_size > 1 and d_size < 10: # filter for parameters to include
                disc.append(p_summary)
                d_sofar += d_size

    global CONFIG_JSON
    with open(os.path.join(dataset, "CONFIG_JSON"), "w") as fp:
        json.dump(dict(disc=disc, cont=cont), fp, default=vars, indent=1)

    # for p in l[:1000]:
    #     if not p.is_continuous():
    #         print(f"{p.name} ({len(p.values)}): [{min(p.values)},{max(p.values)}], m={mean(p.values)}, std={stdev(p.values)}, continuous={p.is_continuous()}")

def load_params(config):

    with open(config, "r") as fp:
        params = json.load(fp)
        discd = params["disc"]
        contd = params["cont"]

        cont, disc = {},{}

        for c in contd:
            cont[c['name']] = c
        for d in discd:
            disc[d['name']] = d

        return cont, disc


def build_vectors(dataset):

    global CONFIG_JSON
    cont, disc = load_params(os.path.join(dataset, "CONFIG_JSON"))

    out_dir = os.path.join(dataset, "nattribs")
    os.makedirs(out_dir, exist_ok=True)
    global PCOUNT

    # vals = []

    for attribs, file_name in attr_it(dataset):

        c_values, c_pmask, d_values, d_pmask = [],[],[],[]

        for _, meta in cont.items():
            if meta['name'] in attribs:
                v = attribs[meta['name']]
                v = (v- meta['mean']) / meta['std']
                # vals.append(v)
                c_values.append(v) # dict(name=meta['name'], value = v, present=True))
                c_pmask.append(1)
            else:
                c_values.append(0) # dict(name=meta['name'], present=False))
                c_pmask.append(0)

        for _, meta in disc.items():

            miin, maax = meta["min"], meta["max"]
            ange = maax - miin + 1

            if meta['name'] in attribs:

                v = attribs[meta['name']] - miin

                for i in range(ange):
                    d_values.append(1 if i == v else 0) # dict(name=meta['name'], present=False))
                    d_pmask.append(1)
            else:
                for i in range(ange):
                    d_values.append(0) # dict(name=meta['name'], present=False))
                    d_pmask.append(0)

        while len(d_values) < PCOUNT: # pad to vector length
            d_values.append(0)  # dict(name=meta['name'], present=False))
            d_pmask.append(0)

        with open(os.path.join(out_dir, Path ( file_name ).with_suffix(".npy")), "wb") as fp:
            np.save( fp, np.array([ c_values, c_pmask, d_values, d_pmask] )) # target value, present-mask

    # print(f"mean is {mean(vals)} std is {stdev(vals)}")


def recover(dataset):

    global CONFIG_JSON
    cont, disc = load_params(os.path.join(dataset, "CONFIG_JSON"))

    for f in glob( f"{dataset}/nattribs/*.npy"):
        print(f)
        x = np.load(f)
        c_values, c_pmask, d_values, d_pmask = x[0], x[1], x[2], x[3]

        print(">>>>> continuous vars")
        i = 0
        for _, meta in cont.items():

            v = c_values[i] * meta["std"] + meta["mean"]

            if c_pmask[i] > 0:
                print(f" {meta['name']} = {v}")

            i += 1

        print (">>>>> discontinuous vars")
        pos = 0
        for _, meta in disc.items():

            miin, maax = meta["min"], meta["max"]
            ange = maax - miin + 1

            if d_pmask[pos] == 0:
                continue

            v = np.argmax(d_values[pos:pos+ange])

            print(f" {meta['name']} = {v}")

            pos += ange


if __name__ == "__main__":

    dataset=sys.argv[1] # "/home/twak/data/dataset_out"
    build_config(dataset)
    build_vectors(dataset)
    # recover(dataset)
