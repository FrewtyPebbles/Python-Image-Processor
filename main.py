from image import ImageProcessor

if __name__ == "__main__":
    img = ImageProcessor("testimage.jpg")
    print("Processing...")
    img.mosaic(100, True).save("testimageEDIT.png")
    print("Done!")