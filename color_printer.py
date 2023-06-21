import main as m
from colorsys import hls_to_rgb
from random import randint
import sys
import requests, argparse

OUTPUT_FOLDER = 'color_swatches'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', dest="total", type=int, default=5, help="how many colors :D")
    parser.add_argument('-t', '--type', dest="COLORMODEL", type=str, choices=["rgb", "hsl"], default="hsl", help="Uses random rgb or adjacent hsl values. Defaults rgb")
    parser.add_argument('-m', '--mode', dest="MODE", type=str, choices=["mono", "mono-dark", "mono-light", "analogic", "complement", "analogic-complement"], default="analogic-complement", helper="Pick the mode to generate colors from")
    args = parser.parse_args()
    uri = "www.thecolorapi.com"
    
    colors = []
    hsl1 = m.set_hsl_color()
    
    for x in range(args.total):                     
        if ((randint(1,500) * x) % args.total) == 0: 
            colors.append(m.find_adj_hsl_color(hsl1))
        else:
            colors.append(m.find_opp_hsl_color(hsl1))
    print(requests.get(f"https://{uri}/scheme?mode={args.MODE}&count={args.total}&format=html&hsl={colors[0].to_string()}").url)

if __name__ == "__main__":
    sys.exit(main())