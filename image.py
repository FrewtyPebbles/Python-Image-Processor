import math
from PIL import Image
from numpy import array
import numpy as np

VER = "0.2.1"

class ImageProcessor:
    def __init__(self, image: str) -> None:
        self.image = Image.open(image)
        self.matrix = array(self.image)

    def desaturate(self, percent, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            num_of_cols = len(row)
            for cn, column in enumerate(row):
                average = sum(column)/len(column)
                self.matrix[rn, cn] = [column[0] + \
                    (average - column[0])*percent, column[1] + \
                    (average - column[1])*percent, column[2] + \
                    (average - column[2])*percent, 255]
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Desaturating Image [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Desaturating Image [100%]")
        return self

    def saturate(self, percent, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                average = (int(column[0]) + int(column[1]) + int(column[2]))/3
                for cvn, col_val in enumerate(column):
                    if col_val > average:
                        self.matrix[rn, cn,
                                    cvn] += (225 - float(col_val))*percent
                    else:
                        self.matrix[rn, cn, cvn] -= float(col_val)*percent
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Saturating Image [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Saturating Image [100%]")
        return self

    def bnw(self, threshold, show_progress=False):
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                average = (int(column[0]) + int(column[1]) + int(column[2]))/3
                if len(self.matrix[rn, cn]) == 3:
                    if average > threshold:
                        self.matrix[rn, cn] = [255, 255, 255]
                    else:
                        self.matrix[rn, cn] = [0, 0, 0]
                else:
                    if average > threshold:
                        self.matrix[rn, cn] = [255, 255, 255, 255]
                    else:
                        self.matrix[rn, cn] = [0, 0, 0, 255]
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Black & White [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Black & White [100%]")
        return self

    def _get_avg_shades(self, threshold, show_progress=False):
        shades = []
        num_of_rows = len(self.matrix)
        last_percent = -1
        current_average = []
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                avg_shade = sum(column)/len(column)
                diff = []
                avg_diff = 0
                if len(current_average) == 0:
                    current_average = column
                    continue
                else:
                    diff = [abs(int(column[i]) - int(current_average[i]))
                            for i in range(0, len(column))]
                    avg_diff = sum(diff)/len(diff)
                if avg_diff < threshold:
                    current_average = [((int(current_average[col_ind]) + int(column[col_ind]))/2)
                                       for col_ind in range(0, len(column))]
                else:
                    shades.append(current_average)
                    current_average = column
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f"   Getting Shades [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f"   Getting Shades [100%]")
        return shades

    def _get_closest_shade(self, shades, current_shade, show_progress=False):
        closest_shade = []
        last_difference = 255
        for sn, shade in enumerate(shades):
            current_diff = 0
            diff = []
            avg_diff = 0
            if len(closest_shade) == 0:
                closest_shade = shade
                continue
            else:
                diff = [abs(int(shade[i]) - int(current_shade[i]))
                        for i in range(0, len(shade))]
                avg_diff = sum(diff)/len(diff)
            if avg_diff < last_difference:
                closest_shade = shade
                last_difference = avg_diff
        return closest_shade

    def cellshade(self, threshold, show_progress=False):
        shades = self._get_avg_shades(threshold, show_progress)
        # print(shades)
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            self.matrix[rn] = [self._get_closest_shade(
                shades, self.matrix[rn, cn], show_progress) for cn in range(0, len(row))]

            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Cell Shading [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Cell Shading [100%]")
        return self


    def downscale(self, pixel_size:int, show_progress=False):
        num_of_rows = len(self.matrix)
        last_percent = -1
        ret_matrix = []
        for rn, row in enumerate(self.matrix):
            if rn%pixel_size == 0:
                row_buffer = []
                for cn, column in enumerate(row):
                    if cn%pixel_size == 0:
                        row_buffer.append(column)
                ret_matrix.append(row_buffer)
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Downscaling [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Downscaling [100%]")
        return ret_matrix

    def mosaic(self, pixel_size:int, show_progress=False):
        num_of_rows = len(self.matrix)
        last_percent = -1
        blur_matrix = self.downscale(pixel_size, show_progress)
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                self.matrix[rn, cn] = blur_matrix[math.floor(rn/pixel_size)][math.floor(cn/pixel_size)]
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Mosaic [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Mosaic [100%]")
        return self

    def contrast(self, percent, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            self.matrix[rn] = [[(col_val + ((255 - float(col_val)) * percent) if col_val > 127.5 else col_val - (
                (float(col_val)) * percent)) for col_val in column] for column in row]
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Contrasting Image [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Contrasting Image [100%]")
        return self

    def decontrast(self, percent, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        for rn, row in enumerate(self.matrix):
            self.matrix[rn] = [[(col_val - ((float(col_val) - 127.5) * percent) if col_val > 127.5 else col_val + (
                (127.5 - float(col_val)) * percent)) for col_val in column] for column in row]

            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Decontrasting Image [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Decontrasting Image [100%]")
        return self

    def mosaic_blur(self, itterations:int, intensity = 3, show_progress=False):
        last_percent = -1
        for i in range(2, itterations):
            self.mosaic_screen(intensity, i, False)
            if last_percent != int(i/itterations*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Mosaic Blur [{int(i/itterations*100)}%]")
            last_percent = int(i/itterations*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Mosaic Blur [100%]")
        return self

    def mosaic_screen(self, percent:int, pixel_size:int, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        blur_matrix = self.downscale(pixel_size, show_progress=False)
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                for cvn, col_val in enumerate(column):
                    #print(int(blur_matrix[math.floor(rn/intensity)][math.floor(cn/intensity)][cvn]) - int(col_val))
                    self.matrix[rn, cn, cvn] = ((int(blur_matrix[math.floor(rn/pixel_size)][math.floor(cn/pixel_size)][cvn]*percent)) + int(col_val))/(1 + percent)
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Mosaic Screen [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Mosaic Screen [100%]")
        return self
    
    def trippy_pixel(self, percent:int, pixel_size:int, show_progress=False):
        percent /= 100
        num_of_rows = len(self.matrix)
        last_percent = -1
        blur_matrix = self.downscale(pixel_size, show_progress=False)
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                for cvn, col_val in enumerate(column):
                    #print(int(blur_matrix[math.floor(rn/intensity)][math.floor(cn/intensity)][cvn]) - int(col_val))
                    self.matrix[rn, cn, cvn] += ((int(blur_matrix[math.floor(rn/pixel_size)][math.floor(cn/pixel_size)][cvn] * percent)) + int(col_val))/(1+percent)
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Trippy Blur [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Trippy Blur [100%]")
        return self

    def save(self, save_as: str):
        save_image = Image.fromarray(self.matrix.astype(np.uint8))
        save_image.save(save_as)
        return self



