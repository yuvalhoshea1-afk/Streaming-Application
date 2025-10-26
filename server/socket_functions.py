import socket
import pickle
import time
import io
import numpy as np
from PIL import Image


HEADER_LENGTH = 10
CREATE_USER = "CREATE_USER"
LOGIN_USER = "LOGIN_USER"
ASK_FOR_VIDEOS_AVAILABLE = "ASK_FOR_VIDEOS_AVAILABLE"
ADK_FOR_VIDEO_DETAILS = "ADK_FOR_VIDEO_DETAILS"
ASK_FOR_FRAME = "ASK_FOR_FRAME"
CHANGE_VIDEO_LOCATION = "CHANGE_VIDEO_LOCATION"
VIDEO_THUMBNAIL = "VIDEO_THUMBNAIL"
IMAGE_FORMAT = "jpeg"


def make_header(data: bytes):
    """
    :param data: bytes of the data
    :return: the header of the bytes, the length of the data, for 2
    """
    return str(len(data)).zfill(HEADER_LENGTH).encode()


def send_data_through_socket(sock: socket.socket, data):
    """
    :param sock: the socket which will send the data
    :param data: the data, can be int, string, list, etc.
    :return: None, just send the data
    """
    try:
        final_data = pickle.dumps(data)
        final_data = make_header(final_data) + final_data
        sock.sendall(final_data)
    except MemoryError:
        time.sleep(0.001)
        send_data_through_socket(sock, data)


def read_data_from_socket(sock: socket.socket, logger=None) -> tuple:
    """
    :param logger:
    :param sock: the socket which we read from
    :return: a tuple: (True/False, data), the first element is if we got data from the socket, the second
    is the data.
    """
    header = sock.recv(HEADER_LENGTH)
    if not header:
        return False, None
    size = int(header.decode())

    data = bytearray()
    while len(data) < size:
        packet = sock.recv(size - len(data))
        data.extend(packet)

        if logger is not None:
            logger.debug(f"data length is {len(data)}")

    data = pickle.loads(data)
    return True, data


def decode_img(img_bytes: bytes) -> np.ndarray:
    """
    :param img_bytes: bytes of a jpeg image (It supposed to work for all kinds of pictures but it should get
    only jpeg according to the protocol).
    :return: Convert the bytes to a np.array of the image
    """
    img_bytes = io.BytesIO(img_bytes)
    with Image.open(img_bytes) as img:
        img_arr = np.asarray(img)
    return img_arr


def encode_img(img_array: np.ndarray) -> bytes:
    """
    :param img_array: array of the image.
    :return: Encode the array into bytes with jpeg.
    """
    img_bytes = io.BytesIO()
    img_pil = Image.fromarray(img_array)
    img_pil.save(img_bytes, format=IMAGE_FORMAT)
    bytes_to_send = img_bytes.getvalue()
    return bytes_to_send
