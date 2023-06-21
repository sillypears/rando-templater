from PIL import Image
from random import randint, choice, random
import os,glob
import sys
from natsort import natsorted
import cv2
import json
import argparse
import progressbar
from colorsys import hls_to_rgb
import requests
from secrets import choice

from copy import deepcopy

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
    def __init__(self, h: int, s: int, l:int):
        self.hue = h
        self.sat = s
        self.lum = l
        self.mode = "hsl"
    
    def to_string(self) -> str:
        return f"hsl({self.hue}, {self.sat}%, {self.lum}%)"
    
    def to_tuple(self) -> tuple:
        return (self.hue, self.sat, self.lum)
    
    def to_hex(self) -> str:
        r = hls_to_rgb(self.hue/360, self.sat/100, self.lum/100)
        print(r, round(r[0]*255),round(r[1]*255),round(r[2]*255))
        return '#{:02x}{:02x}{:02x}'.format(round(r[0]*255),round(r[1]*255),round(r[2]*255))
        
    def __str__(self) -> str:
        return f"({self.hue/360}, {self.sat/100}, {self.lum/100})"

class RGB_Color(object):
    def __init__(self, r, g, b, a):
        self.red = r
        self.gre = g
        self.blu = b
        self.alp = a
        self.mode = 'rgb'

    def to_string(self) -> str:
        return (self.red, self.blu, self.gre, self.alp)

    def to_tuple(self) -> tuple:
        return (self.r, self.g, self.g, self.alp)

    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.blu, self.gre)
    
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

def get_color_api_from_base(color: HSL_Color|RGB_Color, count: int, mode: str) -> list:
    color_list = []

    res = requests.get(f"https://www.thecolorapi.com/scheme?mode={mode}&count={count}&format=json&{color.mode}={color.to_string()}")
    if res.status_code == 200:
        try: 
            for color in res.json()['colors']:
                color_list.append(HSL_Color(color['hsl']['h'], color['hsl']['s'], color['hsl']['l']))
        except Exception as e:
            print(f"Color get error: {e}")

    return color_list
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--num', default=1, dest="HOWMANY", type=int, help="How many times to run")
    parser.add_argument('-s', '--sculpt', dest="SCULPTNAME", type=str, required=True, help="The name of the folder that has the layers to use")
    parser.add_argument('-t', '--type', dest="COLORMODEL", type=str, choices=["rgb", "hsl"], default="rgb", help="Uses random rgb or adjacent hsl values. Defaults rgb")
    parser.add_argument('-m', '--mode', dest="MODE", type=str, choices=["mono", "mono-dark", "mono-light", "analogic", "complement", "analogic-complement"], default="analogic-complement", help="Pick the mode to generate colors from")
    parser.add_argument('-c', '--count', dest="COUNT", type=int, default=5, help="Total number of colors to generate")
    args = parser.parse_args()

    NAME = f"{args.SCULPTNAME}"
    LAYERS = glob.glob(f"sculpts/{NAME}/layer*.png")
    NUMFILES = len(LAYERS)

    print(f"running {args.HOWMANY} times.")
    # for x in range(int(args.HOWMANY)):
    for x in progressbar.progressbar(range(int(args.HOWMANY))):
        OUTPUTFOLDERNUM = 1
        OUTPUTFOLDER = f"sculpts/{NAME}/output{OUTPUTFOLDERNUM}"
        if glob.glob(f"sculpts/{NAME}/output*"):
            OUTPUTFOLDERNUM = int("".join([x for x in natsorted(glob.glob(f"sculpts/{NAME}/output*"))[-1] if x.isdigit()]))
            OUTPUTFOLDER = f"sculpts/{NAME}/output{OUTPUTFOLDERNUM+1}"

        os.makedirs(f"{OUTPUTFOLDER}")
        if not os.path.exists(f"sculpts/{NAME}/finals"): os.mkdir(f"sculpts/{NAME}/finals")

        overlay = Image.open(f"sculpts/{NAME}/overlay.png").convert("RGBA")
        imagenum = 0

        base_color = set_rgb_color() if args.COLORMODEL == "rgb" else set_hsl_color()
        colors = get_color_api_from_base(color=base_color, count=len(natsorted(glob.glob(f"sculpts/{NAME}/layer*.png"))), mode=args.MODE)
        color_list = deepcopy(colors)
        for filenum in natsorted(glob.glob(f"sculpts/{NAME}/layer*.png")):
            imagenum += 1
            layer = Image.open(f"{filenum}").convert("RGBA")
            layer_color = Image.new("RGBA", (layer.width, layer.height))
            color = colors.pop(colors.index(choice(colors)))

            layer_color.paste(
                    color.to_string(),
                    (0,0, layer.width, layer.height)
                )
            layer_color.paste(layer, (0,0), layer)
            layer_color.save(f"{OUTPUTFOLDER}/outimage{imagenum}.png")
            src = cv2.imread(f"{OUTPUTFOLDER}/outimage{imagenum}.png")
            tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
            b, g, r = cv2.split(src)
            rgba = [b, g, r, alpha]
            dst = cv2.merge(rgba, 4)
            cv2.imwrite(f"{OUTPUTFOLDER}/outimage{imagenum}.png", dst)

        outimage = Image.new("RGBA", (overlay.width, overlay.height))
        for filenum in glob.glob(f"{OUTPUTFOLDER}/*"):
            layer = Image.open(filenum)
            outimage.paste(layer, (0,0), layer)

        outimage.paste(overlay, (0,0), overlay)
        outimage.save(f"{OUTPUTFOLDER}/final.png")
        outimage.save(f"sculpts/{NAME}/finals/{NAME}{OUTPUTFOLDERNUM}.png")
        with open (f"{OUTPUTFOLDER}/colors.txt", "w") as w:
            w.write("\n".join(x.to_string() for x in color_list))
            
if __name__ == "__main__":
    sys.exit(main())