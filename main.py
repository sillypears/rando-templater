from PIL import Image
from random import randint
import os,sys

NAME = 'Daisy_Clear_ColorwayTemplate'

NUMFILES = len(os.listdir(NAME))

print(f"There are {NUMFILES} layers")


if not os.path.exists(f"{NAME}/outputs"):
    os.makedirs(f"{NAME}/outputs")


overlay = Image.open(f"{NAME}/overlay.png")
canvas = Image.new("RGBA", (overlay.height, overlay.width))

for filenum in os.listdir(NAME):
    layer = Image.open(f"{NAME}\{filenum}")
    Image.new("RGBA", (layer.height, layer.width))

# overlay = Image.open(IMAGE)
# coloroutput = Image.new("RGBA", (overlay.height, overlay.width))
# overlay = overlay.convert("RGBA")
# coloroutput = coloroutput.convert("RGBA")

# coloroutput.paste((255,255,255), (0,0, coloroutput.width, coloroutput.height))
# total_colors = randint(10,30)
# total_images = randint(30,50)

# folder = f"outputs/{NAME}{randint(0,101010101)}/"
# os.makedirs(folder)

# color_list = []
# for image in range(0, total_images):
#     for colors in range(0, total_colors):

#         color = (randint(0,255), randint(0,255), randint(0,255))
#         outImage = coloroutput.paste(
#             color,
#             (randint(0, overlay.width), randint(0, overlay.height), randint(0, overlay.width), randint(0, overlay.height))
#         )
#         color_list.append(color)
#     coloroutput.paste(overlay, (0,0), overlay)
#     coloroutput.save(f"{folder}/outimage{image}.png")



# print(f"There were a total of {total_images} made")