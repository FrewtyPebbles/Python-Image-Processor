from image import ImageProcessor

if __name__ == "__main__":
    img = ImageProcessor("shelf.png")
    print("Processing...")
    img.mosaic_blur(10, 3, True)\
    .save("shelfEDIT.png")\
    .contrast(50, True)\
    .save("shelfEDIT.png")
    print("Done!")