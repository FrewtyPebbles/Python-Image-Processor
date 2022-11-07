from PIL import Image
from numpy import array
import numpy as np

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

    def _get_max_matrix_vec_len(self, matrix):
        max_len = 0
        for vec in matrix:
            vec_len = len(vec)
            if vec_len > max_len:
                max_len = vec_len
            
        return max_len

    def _get_avg_mosaic(self, pixel_size, show_progress = False):
        num_of_rows = len(self.matrix)
        last_percent = -1
        pix_num_y = len(self.matrix)/pixel_size
        pix_num_x = len(self.matrix[0])/pixel_size
        final_matrix = []
        matrix_buffer_1 = []
        row_buffer = []
        for rn, row in enumerate(self.matrix):
            column_buffer = []
            for cn, col in enumerate(row):
                if len(column_buffer):
                    column_buffer = [(int(column_buffer[cvn]) + int(col_val)) for cvn, col_val in enumerate(col)]
                else:
                    column_buffer = col
                if cn % pixel_size == 0:
                    row_buffer.append(column_buffer)
                    column_buffer = []
            matrix_buffer_1.append(row_buffer)
            row_buffer = []
            if rn % pixel_size == 0:
                #print(matrix_buffer_1)
                matrix_buffer_2 = []
                for mb1cn in range(0, self._get_max_matrix_vec_len(matrix_buffer_1)):
                    color_avg = array([])
                    for mb1row in matrix_buffer_1:
                        #if len(mb1row) <= mb1cn: break
                        if len(color_avg):
                            color_avg = array([int((float(color_avg[i])+float(mb1row[mb1cn][i]))/2) for i in range(0, len(color_avg))], dtype = np.uint8)
                            #print(color_avg)
                        else:
                            #print(mb1row[mb1cn])
                            color_avg = mb1row[mb1cn]
                    #print(f"ind {mb1cn} vec({color_avg})")
                    matrix_buffer_2.append(color_avg)
                final_matrix.append(matrix_buffer_2)
                matrix_buffer_1 = []
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f"   Getting Mosaic Shades [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f"   Getting Mosaic Shades [100%]")
            
        return final_matrix
    
    def mosaic(self, pixel_size, show_progress=False):
        num_of_rows = len(self.matrix)

        last_percent = -1
        shades = array(self._get_avg_mosaic(pixel_size, show_progress))
        #print(shades)
        for rn, row in enumerate(self.matrix):
            for cn, column in enumerate(row):
                try:
                    self.matrix[rn][cn] = shades[round(rn/pixel_size)][round(cn/pixel_size)]
                except:
                    self.matrix[rn][cn] = array([255,255,255,255])
            if last_percent != int(rn/num_of_rows*100) and show_progress:
                if last_percent >= 0:
                    print("\033[A\033[A")
                print(f" Mosaic [{int(rn/num_of_rows*100)}%]")
            last_percent = int(rn/num_of_rows*100)
        if show_progress:
            print("\033[A\033[A")
            print(f" Mosaic [100%]")
        #self.matrix = shades
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

    def save(self, save_as: str):
        save_image = Image.fromarray(self.matrix.astype(np.uint8))
        save_image.save(save_as)
        return self


if __name__ == "__main__":
    img = ImageProcessor("shelf.png")
    print("Processing...")
    img.cellshade(100).contrast(10).save("shelfEDIT.png")
    print("Done!")
