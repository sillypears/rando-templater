from PIL import Image
from random import randint
import os

IMAGE = 'fish.png'
NAME = IMAGE.split('.')[0:-1][0]
overlay = Image.open(IMAGE)
coloroutput = Image.new("RGBA", (overlay.height, overlay.width))
overlay = overlay.convert("RGBA")
coloroutput = coloroutput.convert("RGBA")

coloroutput.paste((255,255,255), (0,0, coloroutput.width, coloroutput.height))
total_colors = randint(6,10)
total_images = randint(5,20)

folder = f"outputs/{NAME}{randint(0,101010101)}/"
os.makedirs(folder)

color_list = []
for image in range(0, total_images):
    for colors in range(0, total_colors):

        color = (randint(0,255), randint(0,255), randint(0,255))
        outImage = coloroutput.paste(
            color,
            (randint(0, overlay.width), randint(0, overlay.height), randint(0, overlay.width), randint(0, overlay.height))
        )
        color_list.append(color)
    coloroutput.paste(overlay, (0,0), overlay)
    coloroutput.save(f"{folder}/outimage{image}.png")



print(f"There were a total of {total_images} made")