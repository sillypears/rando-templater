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
from typing import TextIO
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

MODE_CHOICES=["monochrome", "monochrome-dark", "monochrome-light", "analogic", "complement", "analogic-complement", "random"]


class HSL_Color(object):
    def __init__(self, h: int, s: int, l:int, mode:str="hsl", name=None, hex=None):
        self.hue = h
        self.sat = s
        self.lum = l
        self.mode = mode
        self.name = name
        self.hex = hex
         
    def to_string(self) -> str:
        return f"hsl({self.hue},{self.sat}%,{self.lum}%)"
    
    def to_web_string(self) -> str:
        return f"{self.hue},{self.sat}%,{self.lum}%"
    
    def to_tuple(self) -> tuple:
        return (self.hue, self.sat, self.lum)
    
    def to_hex(self) -> str:
        r = hls_to_rgb(self.hue/360, self.sat/100, self.lum/100)
        return '#{:02x}{:02x}{:02x}'.format(round(r[0]*255),round(r[1]*255),round(r[2]*255))
        
    def __str__(self) -> str:
        return f"{self.name}/{self.hex} => {self.hue} {self.sat} {self.lum}"

    def __repr__(self) -> str:
        return f"{self.name}/{self.hex} => {self.hue} {self.sat} {self.lum}"


class RGB_Color(object):
    def __init__(self, r:int, g:int, b:int, a:int, mode:str="rgb", name:str=None, hex:str=None):
        self.red = r
        self.gre = g
        self.blu = b
        self.alp = a
        self.mode = mode
        self.name = name
        self.hex = hex

    def to_string(self) -> str:
        return f"rgb({self.red},{self.blu},{self.gre},{self.alp})"

    def to_web_string(self) -> str:
        return f"{self.red},{self.gre},{self.blu}"
    
    def to_tuple(self) -> tuple:
        return (self.red, self.gre, self.blu, self.alp)

    def to_hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.blu, self.gre)
    
    def __str__(self) -> str:
        return f"{self.name}/{self.hex} => {self.red} {self.gre} {self.blu} {self.alp}"
    
    def __repr__(self) -> str:
        return f"{self.name}/{self.hex} => {self.red} {self.gre} {self.blu} {self.alp}"
    
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
   # print(f"https://www.thecolorapi.com/scheme?mode={mode}&count={count}&format=json&{color.mode}={color.to_string()}")
    if res.status_code == 200:
        try: 
            for color in res.json()['colors']:
                if mode == "rgb":
                    color_list.append(RGB_Color(color['rgb']['r'], color['rgb']['g'], color['rgb']['b'], 0, color['name']['value'], color['name']['closest_named_hex']))
                else:
                    color_list.append(HSL_Color(color['hsl']['h'], color['hsl']['s'], color['hsl']['l'], color['name']['value'], color['name']['closest_named_hex']))
        except Exception as e:
            print(f"Color get error: {e}")

    return color_list

def get_random_colors(count: int) -> list:
    color_list = []

    for c in range(count):
        try: 
            color_list.append(set_hsl_color())
        except Exception as e:
            print(f"Color get error: {e}")
    return color_list

def set_rgb_to_base(base: str) -> RGB_Color:
    color = ""

    res = requests.get(f"https://www.thecolorapi.com/id?hex={base}&format=json")
    if res.status_code == 200:
        try:
            c = res.json()
            color = RGB_Color(r=c['rgb']['r'], g=c['rgb']['g'], b=c['rgb']['b'], a=255)

        except Exception as e:
            print("Couldn't convert color: {res.status_code}, {res.text}")
    return color

def set_hsl_to_base(base: str) -> HSL_Color:
    color = ""

    res = requests.get(f"https://www.thecolorapi.com/id?hex={base}&format=json")
    if res.status_code == 200:
        try:
            c = res.json()
            color = HSL_Color(h=c['hsl']['h'], s=c['hsl']['s'], l=c['hsl']['l'])
        except Exception as e:
            print("Couldn't convert color: {res.status_code}, {res.text}")
    return color

def get_color_from_hex(hex: str, args) -> HSL_Color:
    color = ""
    # print(hex)
    res = requests.get(f"https://www.thecolorapi.com/id?hex={hex}&format=json")
    if res.status_code == 200:
        try:
            c = res.json()
            color = HSL_Color(h=c['hsl']['h'], s=c['hsl']['s'], l=c['hsl']['l'])
        except Exception as e:
            print("Couldn't convert color: {res.status_code}, {res.text}")
    return color

def get_output_count(f) -> int:
    with open(f, "r") as r:
        try:
            count = int(r.read())
        except:
            sys.exit(f"Couldn't get count number")
    return count

def increase_output_count(f) -> int:
    with open(f, "r") as r:
        try:
            count = int(r.read())
            count += 1
        except Exception as e:
            sys.exit("Couldn't read and increment count: e")
    with open(f, "w") as w:
        w.write(f"{count}")
    return count
    
def run_as_colorlist(args) -> None:
    # print(args.COLORLIST)
    final_list = []
    COLORLIST = args.COLORLIST.split(",")
    #cecea3,#8ac4be,#c6a2bd,#a546be,#c1bfb6
    # print(COLORLIST)
    for color in COLORLIST:
        if color[0] == "#":
            final_list.append(get_color_from_hex(color[1:], args))
        else:
            final_list.append(get_color_from_hex(color, args))

    # print(final_list)
    return final_list

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--num', default=1, dest="HOWMANY", type=int, help="How many times to run")
    parser.add_argument('-s', '--sculpt', dest="SCULPTNAME", type=str, required=True, help="The name of the folder that has the layers to use")
    parser.add_argument('-t', '--type', dest="COLORMODEL", type=str, choices=["rgb", "hsl"], default="hsl", help="Uses random rgb or adjacent hsl values. Defaults rgb")
    parser.add_argument('-m', '--mode', dest="MODE", type=str, choices=MODE_CHOICES, default=None, help="Pick the mode to generate colors from")
    parser.add_argument('-c', '--count', dest="COUNT", type=int, default=None, help="Total number of colors to generate")
    parser.add_argument('-b', '--basecolor', dest="BASECOLOR", type=str, default="", help="Base color to start with")
    parser.add_argument('-l', '--colorlist', dest="COLORLIST", type=str, default=[], help="A list of hexcodes to use as the color list. ex: #11111")
    args = parser.parse_args()

    NAME = f"{args.SCULPTNAME}"
    LAYERS = glob.glob(f"sculpts/{NAME}/layer*.png")
    if not os.path.exists(f"sculpts/{NAME}/output_count.txt"):
        with open(f"sculpts/{NAME}/output_count.txt", "w") as f:
            f.write(f"0")
    OUTPUT_COUNT = f"sculpts/{NAME}/output_count.txt"
    NUMFILES = len(LAYERS)

    
    print(f"running {args.HOWMANY} times.")
    # for x in range(int(args.HOWMANY)):
    for x in progressbar.progressbar(range(int(args.HOWMANY))):
        OUTPUTFOLDERNUM = increase_output_count(OUTPUT_COUNT)
        OUTPUTFOLDER = f"sculpts/{NAME}/output-{OUTPUTFOLDERNUM}"

        os.makedirs(f"{OUTPUTFOLDER}")
        if not os.path.exists(f"sculpts/{NAME}/finals"): os.mkdir(f"sculpts/{NAME}/finals")
        
        COLOR_LIST_OUTPUT = f"sculpts/{NAME}/finals/colors_by_id.txt"
        with open(COLOR_LIST_OUTPUT, 'a'):
            try:
                os.utime(COLOR_LIST_OUTPUT, None)
            except:
                pass
        overlay = Image.open(f"sculpts/{NAME}/overlay.png").convert("RGBA")
        imagenum = 0

        if args.BASECOLOR == "":
            base_color = set_rgb_color() if args.COLORMODEL == "rgb" else set_hsl_color()
        else:
            base_color = set_rgb_to_base(args.BASECOLOR) if args.COLORMODEL == "rgb" else set_hsl_to_base(args.BASECOLOR)
        
        if args.MODE:
            mode = args.MODE
        else:
            mode = choice(MODE_CHOICES)
        
        if args.COUNT:
            count = int(args.COUNT)
        else:
            count = len(natsorted(glob.glob(f"sculpts/{NAME}/layer*.png")))
        if mode != "random":
            colors = get_color_api_from_base(color=base_color, count=count, mode=mode)
        else:
            colors = get_random_colors(count=count)
        if args.BASECOLOR:
            colors.pop(0)
            colors.insert(0, base_color)

        if args.COLORLIST:
            colors = run_as_colorlist(args)
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
            layer_color.save(f"{OUTPUTFOLDER}/outimage-{imagenum}.png")
            src = cv2.imread(f"{OUTPUTFOLDER}/outimage-{imagenum}.png")
            tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
            b, g, r = cv2.split(src)
            rgba = [b, g, r, alpha]
            dst = cv2.merge(rgba, 4)
            cv2.imwrite(f"{OUTPUTFOLDER}/outimage-{imagenum}.png", dst)

        outimage = Image.new("RGBA", (overlay.width, overlay.height))
        for filenum in glob.glob(f"{OUTPUTFOLDER}/*"):
            layer = Image.open(filenum)
            outimage.paste(layer, (0,0), layer)

        outimage.paste(overlay, (0,0), overlay)
        outimage.save(f"{OUTPUTFOLDER}/final.png")
        outimage.save(f"sculpts/{NAME}/finals/{NAME}-{OUTPUTFOLDERNUM}.png")
        with open (f"{OUTPUTFOLDER}/colors.txt", "w") as w:
            w.write("\n".join(x.to_string() for x in color_list))
        with open(COLOR_LIST_OUTPUT, 'a') as w:
            cl_list = ",".join(x.to_hex() for x in color_list)
            w.write(f"{NAME}-{OUTPUTFOLDERNUM}: {cl_list}\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())