from image import ImageProcessor

if __name__ == "__main__":
    img = ImageProcessor("testimg.jpg")
    print("Processing...")
    img.mosaic_blur(20, 10, True)\
    .save("testimgEDIT.jpg")\
    .contrast(50, True)
    print("Done!")