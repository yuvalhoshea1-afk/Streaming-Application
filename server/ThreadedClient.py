import socket
import threading
import time
import functools
import cv2
from PIL import Image
import numpy as np
from ServerConfig import logger, ALL_VIDEOS_DIRECTORIES, get_video_and_thumbnail_path
import socket_functions
from socket_functions import read_data_from_socket, send_data_through_socket
from database import User


class ClientThread(threading.Thread):

    def __init__(self, client_sock: socket.socket, client_addr: tuple):
        super().__init__(daemon=True)
        self.__sock = client_sock
        self.__addr = client_addr
        self.__cap = None

    def run(self) -> None:
        """
        :return: None. Running the thread.
        """
        logger.info("Starting new client thread!")
        self.__sock.setblocking(True)
        try:
            while True:
                got_data, data = read_data_from_socket(self.__sock)
                if not got_data:
                    time.sleep(0.001)
                    continue

                logger.debug(f"Got new data from {self.__addr}.")
                self.__handle_data(data)

        except ConnectionResetError:
            logger.info(f"Client {self.__addr} disconnected. ")

    def __handle_data(self, data: list) -> None:
        """
        :param data: The data that the user send to the server.
        :return: None. Handle the data in accordance to the data
        """
        logger.debug(f"Client {self.__addr} said: {data}.")
        # what function does the client wants
        func = data[0]

        switch = {
            socket_functions.CREATE_USER: functools.partial(self.__create_user, data),
            socket_functions.LOGIN_USER: functools.partial(self.__check_login, data),
            socket_functions.ASK_FOR_VIDEOS_AVAILABLE: self.__get_videos_list,
            socket_functions.ADK_FOR_VIDEO_DETAILS: functools.partial(self.__get_show_details, data),
            socket_functions.ASK_FOR_FRAME: functools.partial(self.__get_frame, data),
            socket_functions.CHANGE_VIDEO_LOCATION: functools.partial(self.__change_frame_location, data)
        }

        switch[func]()

    def __create_user(self, data):
        username = data[1]
        password = data[2]
        if User.find(username) is None:  # user does not exists - good
            User.add_user(username, password)
            send_data_through_socket(self.__sock, [socket_functions.CREATE_USER, True])
        else:  # username already exists
            send_data_through_socket(self.__sock, [socket_functions.CREATE_USER, False])

    def __check_login(self, data):
        username = data[1]
        password = data[2]

        is_ok = User.valid_user(username, password)
        send_data_through_socket(self.__sock, [socket_functions.LOGIN_USER, is_ok])

    def __get_videos_list(self) -> None:
        """
        :return: None. sednd list of all the videos available
        """
        # videos available are the list that in the variable ALL_VIDEOS, send a list of all of them
        send_data_through_socket(self.__sock, [socket_functions.ASK_FOR_VIDEOS_AVAILABLE, list(ALL_VIDEOS_DIRECTORIES)])
        # send thumbnails
        for vid_dir in ALL_VIDEOS_DIRECTORIES:
            _, thumbnail_path = get_video_and_thumbnail_path(vid_dir)
            with Image.open(thumbnail_path) as img:
                encoded_img = socket_functions.encode_img(np.array(img))
                send_data_through_socket(self.__sock, [socket_functions.VIDEO_THUMBNAIL, vid_dir, encoded_img])

    def __get_show_details(self, data: list) -> None:
        """
        :param data: The data that the user send. Contains the video which he selected.
        :return: None. Send video details (fps and how many frames) to the client.
        """
        vid = data[1]
        vid_path, _ = get_video_and_thumbnail_path(vid)
        if self.__cap is None:
            self.__cap = cv2.VideoCapture(vid_path)

        fps = self.__cap.get(cv2.CAP_PROP_FPS)
        frames_amount = self.__cap.get(cv2.CAP_PROP_FRAME_COUNT)

        logger.debug("Send video details!")
        send_data_through_socket(self.__sock, [socket_functions.ADK_FOR_VIDEO_DETAILS, (fps, frames_amount)])

    def __get_frame(self, data: list):
        """
        :param data: The data that the client sent.
        :return: None. Send the next frame to the client.
        """
        video = data[1]
        video, _ = get_video_and_thumbnail_path(video)

        if self.__cap is None:
            self.__cap = cv2.VideoCapture(video)
        elif not self.__cap.isOpened():
            self.__cap = cv2.VideoCapture(video)

        ret, img_frame = self.__cap.read()

        if ret:
            img_bytes = socket_functions.encode_img(img_frame)
            send_data_through_socket(self.__sock, [socket_functions.ASK_FOR_FRAME, img_bytes])

    def __change_frame_location(self, data: list):
        """
        :param data: The data that the user sent to the client.
        :return: None. Make a new cap from the new location and sending approval to the client.
        """
        vid_name = data[1]
        frame_index = data[2]
        video_location, _ = get_video_and_thumbnail_path(vid_name)

        self.__cap = cv2.VideoCapture(video_location)
        # set the cap to display frames from "frame_index" and forward.
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        send_data_through_socket(self.__sock, [socket_functions.CHANGE_VIDEO_LOCATION, frame_index])
