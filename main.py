from PIL import Image
from random import randint
import os,glob
from natsort import natsorted
import cv2
import json
import argparse

def set_rgb_color() -> tuple:
    return (randint(0,255), randint(0,255), randint(0,255), randint(100,255))

def find_adj_rgb_color(color: tuple) -> str:

    return 0

def find_opp_rgb_color(color: tuple) -> str:

    return 0

def set_hsl_color() -> str:
    return f"hsl({randint(0,360)}, {randint(0,100)}%, {randint(0,100)}%)"

def find_adj_hsl_color(color: str) -> str:

    return 0

def find_opp_hsl_color(color: str) -> str:

    return 0
 
parser = argparse.ArgumentParser()

parser.add_argument('-n', '--num', default=1, dest="HOWMANY", help="How many times to run")
parser.add_argument('-s', '--sculpt', dest="SCULPTNAME", required=True, help="The name of the folder that has the layers to use")
args = parser.parse_args()

NAME = args.SCULPTNAME
LAYERS = glob.glob(f"{NAME}/layer*.png")
NUMFILES = len(LAYERS)

print(f"running {args.HOWMANY} times.")
for x in range(int(args.HOWMANY)):
    OUTPUTFOLDERNUM = 1
    OUTPUTFOLDER = f"{NAME}/output{OUTPUTFOLDERNUM}"
    if glob.glob(f"{NAME}/output*"):
        OUTPUTFOLDERNUM = int("".join([x for x in natsorted(glob.glob(f"{NAME}/output*"))[-1] if x.isdigit()]))
        OUTPUTFOLDER = f"{NAME}/output{OUTPUTFOLDERNUM+1}"

    os.makedirs(f"{OUTPUTFOLDER}")
    if not os.path.exists(f"{NAME}/finals"): os.mkdir(f"{NAME}/finals")

    overlay = Image.open(f"{NAME}/overlay.png")
    canvas = Image.new("RGBA", (overlay.height, overlay.width))
    color_list = []
    imagenum = 0


    for filenum in glob.glob(f"{NAME}/layer*.png"):
        imagenum += 1
        layer = Image.open(f"{filenum}")
        layer_color = Image.new("RGBA", (layer.height, layer.width))
        color = set_rgb_color()
        outImage = layer_color.paste(
                color,
                (0,0, layer.width, layer.height)
            )
        color_list.append(color)
        layer_color.paste(layer, (0,0), layer)
        layer_color.save(f"{OUTPUTFOLDER}/outimage{imagenum}.png")
        src = cv2.imread(f"{OUTPUTFOLDER}/outimage{imagenum}.png")
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b, g, r, alpha]
        dst = cv2.merge(rgba, 4)
        cv2.imwrite(f"{OUTPUTFOLDER}/outimage{imagenum}.png", dst)
        print(f"Overlaying {filenum} with {color} and saving as outimage{imagenum}.png")

    outimage = Image.new("RGBA", (overlay.height, overlay.width))
    for filenum in glob.glob(f"{OUTPUTFOLDER}/*"):
        layer = Image.open(filenum)
        outimage.paste(layer, (0,0), layer)

    outimage.paste(overlay, (0,0), overlay)
    outimage.save(f"{OUTPUTFOLDER}/final.png")
    outimage.save(f"{NAME}/finals/{NAME}{OUTPUTFOLDERNUM}.png")
    # with open (f"{OUTPUTFOLDER}/colors.txt", "w") as w:
    #     w.write("\n".join('%s,%s,%s' % x for x in color_list))