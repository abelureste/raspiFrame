#!/usr/bin/env python3

import os, time, glob
from PIL import Image
from inky.auto import auto
from flaskServer import Data
from io import BytesIO

print("Displaying your images")

# Set up inky display
try:
    inky_display = auto(ask_user=True, verbose=True)
except NotImplementedError:
    pass

try:
    inky_display.set_border(inky_display.BLACK)
except NotImplementedError:
    pass

# Retrieve image folder path
PATH = os.path.dirname(__file__)
imagePath = os.path.join(PATH, "images/")
print(f"Retrieving images from {imagePath}")
validFormats = ('.jpg','.png')

def printImage():
    imageFiles = Data.query.all()

    if not imageFiles:
        print("No images found")

    else:
        for imageFile in imageFiles:
            try:
                print(f"Displaying: {imageFile.name}")

                img = Image.open(BytesIO(imageFile.file))

                inky_display.set_image(img)
                inky_display.show()

                img.close()
                sleepTime = 30 * 60
                print(f"Sleeping for {sleepTime / 60} minutes...")
                time.sleep(sleepTime)

            except Exception as e:
                print(f"Error displaying {imageFile}: {e}")

# Loops indefinitely
while True:
    printImage()