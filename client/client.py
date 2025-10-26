import functools
import pickle
import socket
import time
import threading
from typing import List

from ClientConfig import logger
from videoplayer import VideoPlayer
import socket_functions
from socket_functions import read_data_from_socket, send_data_through_socket


class Client:

    def __init__(self, ip: str, port: int, video_player: VideoPlayer):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_addr = (ip, port)
        self._video_player = video_player
        self._videos_names = []
        self._active_frames_requests = 0
        self._video_thumbnails = {}
        self.server_ended_changing_video_position = False
        self.created_user = None
        self.logged_in = None

    def threaded_connect_and_listen_to_server(self):
        """
        :return: None, create a thread which is listening to the server
        """
        logger.info(f"Connected to {self._server_addr}.")
        self._sock.connect(self._server_addr)
        print(self._server_addr)
        threading.Thread(target=self.__listen_to_server, daemon=True).start()

    def create_user(self, username: str, password: str) -> None:
        """
        :param username: the username which we create
        :param password: the password of the username
        :return: Asking for creating the username. Returns none.
        """
        send_data_through_socket(self._sock, [socket_functions.CREATE_USER, username, password])

    def login(self, username: str, password: str):
        """
        :param username: the username which we want to login into.
        :param password: the password of the username
        :return: Asking for logging to the username. Returns none.
        """
        send_data_through_socket(self._sock, [socket_functions.LOGIN_USER, username, password])

    def ask_for_all_videos_available(self) -> list:
        """
        :return: a list of all the videos available
        """
        send_data_through_socket(self._sock, [socket_functions.ASK_FOR_VIDEOS_AVAILABLE])
        while not self._videos_names:  # while there are no videos
            # wait for response from the server
            time.sleep(0.001)
        while len(self._video_thumbnails) != len(self._videos_names):  # waiting for the thumbnails
            time.sleep(0.001)
        return self._video_thumbnails

    def ask_for_video_details(self, show: str):
        """
        :param show: the show we are asking its details
        :return: None
        """
        send_data_through_socket(self._sock, [socket_functions.ADK_FOR_VIDEO_DETAILS, show])

    def ask_for_frame(self, video: str) -> None:
        """
        Asking for the next frame at the video.
        :param video: the video we are asking from the server.
        :return: None. Just request the video.
        """
        send_data_through_socket(self._sock, [socket_functions.ASK_FOR_FRAME, video])
        self._active_frames_requests += 1

    def ask_for_new_location(self, vid_name: str, new_location: int):
        """
        Asking to change the location of the video. For example from the 101 frame to the 356 frame.
        :param vid_name: the name of the video.
        :param new_location: the new location we want.
        :return: None. Just request it.
        """
        send_data_through_socket(self._sock, [socket_functions.CHANGE_VIDEO_LOCATION, vid_name, new_location])

    def can_request_frame(self) -> bool:
        """
        :return: bool. Can we ask for more frames from the server.
        """
        have_space = self._active_frames_requests < self._video_player.MAX_FRAMES
        return have_space and self._video_player.can_add_frame()

    def __repr__(self):
        return f"Active frames request: {self._active_frames_requests}."

    def set_video_player(self, video_player: VideoPlayer):
        """
        :param video_player: VideoPlayer object
        setting the VideoPlayer object.
        """
        self._video_player = video_player

    def wait_for_getting_all_requested_frames(self):
        while self._active_frames_requests != 0:
            pass

    def __listen_to_server(self):
        """
        This function needs to run in a thread. Infinite loop of listening to the server and handle with
        data that server sent to the client.
        """
        while True:
            try:
                got_data, data = read_data_from_socket(self._sock, logger)
            except pickle.UnpicklingError as e:
                logger.error(e)
                continue

            if not got_data:
                time.sleep(0.001)
                continue

            logger.debug(f"Got data from server")
            self.__handle_data(data)

    def __handle_data(self, data):
        """
        :param data: the data that the user sent
        :return: None. Handle the data.
        """
        func = data[0]

        switch = {
            socket_functions.CREATE_USER: functools.partial(self.__ask_for_creating_user, data),
            socket_functions.LOGIN_USER: functools.partial(self.__logged_in, data),
            socket_functions.ASK_FOR_VIDEOS_AVAILABLE: functools.partial(self.__ask_for_videos_case, data),
            socket_functions.ADK_FOR_VIDEO_DETAILS: functools.partial(self.__ask_for_details_case, data),
            socket_functions.ASK_FOR_FRAME: functools.partial(self.__ask_for_frame_case, data),
            socket_functions.CHANGE_VIDEO_LOCATION: self.__changed_video_location,
            socket_functions.VIDEO_THUMBNAIL: functools.partial(self.__get_thumbnails, data)
        }

        switch[func]()

    def __ask_for_creating_user(self, data: List):
        added_user = data[1]
        self.created_user = added_user

    def __logged_in(self, data):
        is_ok = data[1]
        self.logged_in = is_ok

    def __ask_for_videos_case(self, data: List):
        """
        :param data: the data the server send to the client. Have a list of all videos inside.
        """
        videos: List = data[1]
        self._videos_names = videos

    def __ask_for_details_case(self, data: List):
        """
        :param data: The data the server sent to the client. Have inside a tuple of fps and how many frames in
        a video.
        """
        fps, frames_amount = data[1]
        self._video_player.set_fps(fps)
        self._video_player.set_frames_amount(frames_amount)

    def __ask_for_frame_case(self, data: List):
        """
        :param data: The data the server sent to the client. Have inside the image encoded as bytes.
        """
        img_bytes = data[1]
        img_frame = socket_functions.decode_img(img_bytes)
        self._video_player.add_frame(img_frame)
        self._active_frames_requests -= 1

    def __changed_video_location(self):
        # when the server said it ended changing the video location
        self.server_ended_changing_video_position = True

    def __get_thumbnails(self, data: List):
        """
        :param data: list of data which sent from the server. Have the video name and thumbnail image
        encoded in bytes
        """
        vid = data[1]
        encoded_img = data[2]
        decoded_img = socket_functions.decode_img(encoded_img)
        self._video_thumbnails[vid] = decoded_img
