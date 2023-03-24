from PIL import Image
from random import randint, choice, random
import os,glob
from natsort import natsorted
import cv2
import json
import argparse

RGB_OPP_THRESH_LOW = 0
RGB_OPP_THRESH_HIGH = 255
RGB_ADJ_THRESH_LOW = 0
RGB_ADJ_THRESH_HIGH = 255
RGB_ALP_THRESH_LOW = 0
RGB_ALP_THRESH_HIGH = 1

HSL_OPP_THRESH_LOW = 160
HSL_OPP_THRESH_HIGH = 190
HSL_ADJ_THRESH_LOW = 20
HSL_ADJ_THRESH_HIGH = 40

class HSL_Color(object):
    def __init__(self, h, s, l):
        self.hue = h
        self.sat = s
        self.lum = l
    
    def to_string(self) -> str:
        return f"hsl({self.hue}, {self.sat}%, {self.lum}%)"

class RGB_Color(object):
    def __init__(self, r, g, b, a):
        self.red = r
        self.gre = g
        self.blu = b
        self.alp = a

    def to_string(self) -> str:
        return (self.red, self.blu, self.gre, self.alp)

    def __str__(self) -> str:
        return f"({self.red}, {self.blu}, {self.gre}, {self.alp})"
    
def set_rgb_color() -> tuple:
    return RGB_Color(
        randint(0,255), 
        randint(0,255),
        randint(0,255), 
        randint(0,255)
    )

def find_adj_rgb_color(color: RGB_Color) -> RGB_Color:

    return RGB_Color(
        randint(RGB_ADJ_THRESH_LOW,RGB_ADJ_THRESH_HIGH), 
        randint(RGB_ADJ_THRESH_LOW,RGB_ADJ_THRESH_HIGH), 
        randint(RGB_ADJ_THRESH_LOW,RGB_ADJ_THRESH_HIGH), 
        randint(RGB_ALP_THRESH_LOW,RGB_ALP_THRESH_HIGH)
    )

def find_opp_rgb_color(color: RGB_Color) -> RGB_Color:

    return RGB_Color(
        randint(RGB_OPP_THRESH_LOW,RGB_OPP_THRESH_HIGH), 
        randint(RGB_OPP_THRESH_LOW,RGB_OPP_THRESH_HIGH), 
        randint(RGB_OPP_THRESH_LOW,RGB_OPP_THRESH_HIGH), 
        randint(RGB_ALP_THRESH_LOW,RGB_ALP_THRESH_HIGH)
    )

def set_hsl_color() -> HSL_Color:
    return HSL_Color(randint(0,360), randint(0,100), randint(0,100))

def find_adj_hsl_color(color: HSL_Color) -> HSL_Color:
    n_h = (randint(HSL_ADJ_THRESH_LOW,HSL_ADJ_THRESH_HIGH)+color.hue)%360
    n_s = (randint(HSL_ADJ_THRESH_LOW,HSL_ADJ_THRESH_HIGH)+color.sat)%360
    n_l = (randint(HSL_ADJ_THRESH_LOW,HSL_ADJ_THRESH_HIGH)+color.lum)%360
    return HSL_Color((randint(HSL_ADJ_THRESH_LOW,HSL_ADJ_THRESH_HIGH)+color.hue)%360, color.sat, color.lum)

def find_opp_hsl_color(color: HSL_Color) -> HSL_Color:
    n_h = (randint(HSL_OPP_THRESH_LOW,HSL_OPP_THRESH_HIGH)+color.hue)%360
    n_s = (randint(HSL_OPP_THRESH_LOW,HSL_OPP_THRESH_HIGH)+color.sat)%360
    n_l = (randint(HSL_OPP_THRESH_LOW,HSL_OPP_THRESH_HIGH)+color.lum)%360
    return HSL_Color((randint(HSL_OPP_THRESH_LOW,HSL_OPP_THRESH_HIGH)+color.hue)%360, color.sat, color.lum)
 
parser = argparse.ArgumentParser()

parser.add_argument('-n', '--num', default=1, dest="HOWMANY", help="How many times to run")
parser.add_argument('-s', '--sculpt', dest="SCULPTNAME", required=True, help="The name of the folder that has the layers to use")
parser.add_argument('-m', '--model', dest="COLORMODEL", choices=["rgb", "hsl"], default="rgb", help="Uses random rgb or adjacent hsl values. Defaults rgb")
args = parser.parse_args()

NAME = f"{args.SCULPTNAME}"
LAYERS = glob.glob(f"sculpts/{NAME}/layer*.png")
NUMFILES = len(LAYERS)

print(f"running {args.HOWMANY} times.")
for x in range(int(args.HOWMANY)):
    OUTPUTFOLDERNUM = 1
    OUTPUTFOLDER = f"sculpts/{NAME}/output{OUTPUTFOLDERNUM}"
    if glob.glob(f"sculpts/{NAME}/output*"):
        OUTPUTFOLDERNUM = int("".join([x for x in natsorted(glob.glob(f"sculpts/{NAME}/output*"))[-1] if x.isdigit()]))
        OUTPUTFOLDER = f"sculpts/{NAME}/output{OUTPUTFOLDERNUM+1}"

    os.makedirs(f"{OUTPUTFOLDER}")
    if not os.path.exists(f"sculpts/{NAME}/finals"): os.mkdir(f"sculpts/{NAME}/finals")

    overlay = Image.open(f"sculpts/{NAME}/overlay.png").convert("RGBA")
    canvas = Image.new("RGBA", (overlay.width, overlay.height))
    color_list = []
    imagenum = 0

    color = set_rgb_color() if args.COLORMODEL == "rgb" else set_hsl_color()
    for filenum in natsorted(glob.glob(f"sculpts/{NAME}/layer*.png")):
        imagenum += 1
        layer = Image.open(f"{filenum}").convert("RGBA")
        layer_color = Image.new("RGBA", (layer.width, layer.height))
        outImage = layer_color.paste(
                color.to_string(),
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
        if randint(0,1):
            color = find_adj_rgb_color(choice(color_list)) if args.COLORMODEL == "rgb" else find_adj_hsl_color(choice(color_list))
        else:
            color = find_opp_rgb_color(choice(color_list)) if args.COLORMODEL == "rgb" else find_opp_hsl_color(choice(color_list))

    # print(",".join(x.to_string() for x in color_list))
        # print(f"Overlaying {filenum} with {color} and saving as outimage{imagenum}.png")
    outimage = Image.new("RGBA", (overlay.width, overlay.height))
    for filenum in glob.glob(f"{OUTPUTFOLDER}/*"):
        layer = Image.open(filenum)
        outimage.paste(layer, (0,0), layer)

    outimage.paste(overlay, (0,0), overlay)
    outimage.save(f"{OUTPUTFOLDER}/final.png")
    outimage.save(f"sculpts/{NAME}/finals/{NAME}{OUTPUTFOLDERNUM}.png")
    with open (f"{OUTPUTFOLDER}/colors.txt", "w") as w:
        w.write("\n".join(x.__str__() for x in color_list))
        