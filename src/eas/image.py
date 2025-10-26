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
    edges = cv.Canny(img, 100, 200)
    ret, img = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
    cv.imwrite("images/canny.jpg", img)

    return edges


if __name__ == "__main__":
    img = canny("images/cat.jpg")
