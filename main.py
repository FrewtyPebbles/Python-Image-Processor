from image import ImageProcessor

if __name__ == "__main__":
    img = ImageProcessor("testimage.jpg")
    print("Processing...")
    img.color_replace((150,150,200),
                    (200,200,255),
                    (0,100,255),
                    True)\
        .color_replace((0,0,0),
                    (50,50,50),
                    (0,0,0),
                    True)\
        .color_replace((205,205,205),
                    (255,255,255),
                    (255,0,0),
                    True)\
        .save("colormaskEdit.jpg")
    print("Done!")