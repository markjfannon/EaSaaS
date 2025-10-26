import numpy as np
import cv2 as cv
from pathlib import Path
from constants import *

current_file_path = Path(__file__).resolve()


def resize_img(img: np.ndarray) -> np.ndarray:
    return cv.resize(img, (RESOLUTION_HORIZONTAL, RESOLUTION_VERTICAL))
    

def canny(img_path: str) -> np.ndarray:
    full_img_path = current_file_path / img_path

    img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    img = resize_img(img)
    img = cv.GaussianBlur(img, (15, 15), 0)  
    edges = cv.Canny(img,100,200)

    return edges

if __name__ == "__main__":
    img = canny("images/cat.jpg")
    cv.imwrite("images/cat_lines.jpg",img)