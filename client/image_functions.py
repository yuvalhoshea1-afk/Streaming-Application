import cv2
import numpy as np
from PyQt5.QtGui import QImage


def resize_image_to_specific_height(img_arr: np.ndarray, wanted_height: int) -> np.ndarray:
    """
    :param img_arr: numpy array of pixels
    :param wanted_height: the height that we the picture to have.
    :return: The new image with the wanted height
    """
    # get the scale
    height, _, _ = img_arr.shape
    scale_percent = wanted_height * 100 / height
    # resize the picture
    new_width = int(img_arr.shape[1] * scale_percent / 100)
    new_height = int(img_arr.shape[0] * scale_percent / 100)
    dim = (new_width, new_height)
    new_array = cv2.resize(img_arr, dim, interpolation=cv2.INTER_AREA)
    return new_array


def convert_numpy_array_to_qimage(img_arr: np.ndarray) -> QImage:
    """
    :param img_arr: image array of pixels
    :return: QImage of the image
    """
    array = np.array(cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB))
    # convert to QImage
    height, width, channel = array.shape
    bytes_per_line = 3 * width
    q_img = QImage(array, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    return q_img


