import os
import process_labels
from pathlib import Path
import json

if __name__ == "__main__":

    for batch in os.listdir("data/photos"):
        # if is dir
        if os.path.isdir(os.path.join("data/photos", batch)):
            for file in os.listdir(f"data/photos/{batch}"):
                ext = os.path.splitext(file)[1]
            if ext[1:].upper() in process_labels.RAW_EXTS:
                good = False
                for jext in ["jpg", "JPG", "jpeg", "JPEG"]:
                    if Path(os.path.join("data/photos", batch, file)).with_suffix("." + jext).exists():
                        good = True
                        break
                if not good:
                    print(f"data/photos/{batch}/{file}")



'''
data/photos/elsayed_port_said_20230125/IMG_5672.CR2
data/photos/elsayed_port_said_20230125/IMG_5673.CR2
data/photos/kubra_istanbul_20220827/003_0718.NEF
data/photos/kubra_istanbul_20220827/003_1421.NEF
data/photos/jan_cebu_20230120/IMG_6384.CR2
data/photos/jan_cebu_20230120/IMG_5524.CR2
data/photos/jan_cebu_20230120/IMG_5473.CR2
data/photos/jan_cebu_20230120/IMG_5490.CR2
data/photos/jan_cebu_20230120/IMG_5641.CR2
data/photos/jan_cebu_20230120/IMG_5474.CR2
data/photos/jan_cebu_20230120/IMG_6188.CR2
data/photos/yuan_dalian_20230323/DSCF1267.RAF
data/photos/sarabjot_newdehli_20230315/DSC06202.ARW
data/photos/sarabjot_newdehli_20230315/DSC06194.ARW
data/photos/sarabjot_newdehli_20230315/DSC06237.ARW
data/photos/sarabjot_newdehli_20230315/DSC06192.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1824.NEF
data/photos/sarabjot_newdehli_20230315/DSC06247.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1822.NEF
data/photos/sarabjot_newdehli_20230315/DSC06226.ARW
data/photos/sarabjot_newdehli_20230315/DSC06233.ARW
data/photos/sarabjot_newdehli_20230315/DSC06243.ARW
data/photos/sarabjot_newdehli_20230315/DSC06246.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1821.NEF
data/photos/sarabjot_newdehli_20230315/DSC06234.ARW
data/photos/sarabjot_newdehli_20230315/DSC06225.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1832.NEF
data/photos/sarabjot_newdehli_20230315/DSC06239.ARW
data/photos/sarabjot_newdehli_20230315/DSC06227.ARW
data/photos/sarabjot_newdehli_20230315/DSC06245.ARW
data/photos/sarabjot_newdehli_20230315/DSC06248.ARW
data/photos/sarabjot_newdehli_20230315/DSC06240.ARW
data/photos/sarabjot_newdehli_20230315/DSC06238.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1825.NEF
data/photos/sarabjot_newdehli_20230315/DSC06242.ARW
data/photos/sarabjot_newdehli_20230315/DSC06199.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1823.NEF
data/photos/sarabjot_newdehli_20230315/DSC_1834.NEF
data/photos/sarabjot_newdehli_20230315/DSC_1826.NEF
data/photos/sarabjot_newdehli_20230315/DSC06236.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1646.NEF
data/photos/sarabjot_newdehli_20230315/DSC06232.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1835.NEF
data/photos/sarabjot_newdehli_20230315/DSC_1828.NEF
data/photos/sarabjot_newdehli_20230315/DSC_1827.NEF
data/photos/sarabjot_newdehli_20230315/DSC06244.ARW
data/photos/sarabjot_newdehli_20230315/DSC06201.ARW
data/photos/sarabjot_newdehli_20230315/DSC_1829.NEF
data/photos/sarabjot_newdehli_20230315/DSC06193.ARW
data/photos/sarabjot_newdehli_20230315/DSC06241.ARW
data/photos/sarabjot_newdehli_20230315/DSC06249.ARW
data/photos/sarabjot_newdehli_20230315/DSC06235.ARW
data/photos/kubra_istanbul_220827/003_0718.NEF
data/photos/kubra_istanbul_220827/003_1421.NEF

'''