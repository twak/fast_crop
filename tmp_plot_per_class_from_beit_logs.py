import glob
import os.path
import re

'''
pull tables out of the default beit2 log... :/
'''


iter = -1

logs = glob.glob("/home/twak/Documents/by_n/*.log")
from pathlib import Path
experiments = {}

for log in logs:
    print (log)
    n = int ( os.path.splitext( Path(log).name )[0] )
    experiments[n] = experiment = {}
    with open(log) as fp:
        for line in fp:

            res = re.search("at\\s([0-9]+)", line)
            if res:
                # print(res.group(1))
                iter = int(res.group(1))
                experiment[iter] = iter_results = {}

            if line.startswith('|'):
                pattern = '\\|[\\s]+([^\\|]+)[\\s]+\\|[\\s]+([\\S]+)[\\s]+\\|[\\s]+([\\S]+)[\\s]+'   # \s\|\s([\S])\s\|\s([\S])\s
                result =  re.search(pattern, line)
                # for g in result.groups():
                key = result.group(1).strip()
                if key == "Class" or key == 'Scope' or key == 'none':
                    pass
                else:
                    iter_results[key] = [float(result.group(2)), float(result.group(3))]


        for iter, r in experiment.items():
            for klass, vals in r.items():
                print(f"{iter}, {klass}, {vals[0]}, {vals[1]}")

classes = [
        "window pane",         "window frame",
        "open-window",
        "wall frame",
        "wall",
        "door",
        "shutter",
        "blind",
        "bars",
        "balcony",
        "misc object", "global" ]

sizes = [860,1540,3080,10000,20000]
iters = []
for i in range (1, 11):
    iters.append(i * 16000)

miou = 0
acc = 1

if False: # mac ( miou or accuracy ) vs dataset size
    print (","+ ", ".join(classes))
    for n in sizes:
        experiment = experiments[n]
        maxx = {}
        for c in classes: maxx[c] = 0
        for iter, r in experiment.items():
            for klass, vals in r.items():
                maxx[klass] = max (maxx[klass], vals[miou]) # miou = 0, accuracy = 1

        print(f"{n}, ", end='')
        for c in classes:
            print(f"{maxx[c]}, ", end='')
        print()
else:
    # single class over time


    klass = classes[2]
    print (klass+","+ ", ".join( list ( map ( lambda x: str(x), iters ))) )

    for n in [860, 1540, 3080, 10000, 20000]:
        experiment = experiments[n]
        print(f"{n}, ", end="")
        for i in list ( experiment.keys() ):
            vals = experiment[i][klass]
            print(f"{vals[acc]}, ", end="") # miou
        print()



