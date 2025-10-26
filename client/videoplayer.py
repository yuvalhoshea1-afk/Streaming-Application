from collections import deque
from typing import Tuple
import cv2
import numpy as np
from ClientConfig import logger


class VideoPlayer:
    MAX_FRAMES = 50
    __NOT_SET = -1

    def __init__(self):
        self._queue = deque()

        self._frames_got_counter = 0
        self._frames_played_counter = 0

        self._time_between_frames_ms = self.__NOT_SET
        self._frames_amount = self.__NOT_SET

        self._no_frames_from_server = False

        self.__scale_percent = 100

    def add_frame(self, img: np.ndarray) -> None:
        """
        :param img: numpy array, the frame we add to the buffer
        :return: None, add the frame to the buffer
        """
        frame = img
        self._queue.append(frame)
        self._frames_got_counter += 1

    def end_of_frames_from_server(self):
        """
        :return: we will not get more frames
        """
        self._no_frames_from_server = True

    def can_add_frame(self):
        """
        :return: bool, can we add more frames to the queue
        """
        return len(self._queue) < self.MAX_FRAMES

    def get_frames(self):
        """
        :return: create generator that return the frames of the video
        """
        while not self.__is_end():
            frame = self.__next_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield self.__resize_img(frame)

            logger.debug(f"Frame {self._frames_played_counter}")

    def __next_frame(self):
        """
        :return: numpy array, the next frame that shown in screen
        """
        while len(self._queue) == 0:
            # waiting to get next frame from server
            pass

        self._frames_played_counter += 1
        return self._queue.popleft()

    def __is_end(self):
        """
        :return: bool, return True if the video ended, else return False
        """
        return self._frames_played_counter >= self._frames_amount-1

    def set_fps(self, fps: int):
        ms_in_sec = 1000
        self._time_between_frames_ms = round(ms_in_sec / fps)

    def set_frames_amount(self, frames_amount: int):
        self._frames_amount = frames_amount

    def wait_for_video_details(self):
        while self.__NOT_SET in (self._time_between_frames_ms, self._frames_amount):
            # wait for video details
            pass

    def __resize_img(self, img: np.ndarray):
        scale_percent = self.__scale_percent  # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize the image
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        return img

    def __repr__(self):
        return f"frames available: {len(self._queue)}, frame shown: {self._frames_played_counter}" \
               f", frames got: {self._frames_got_counter}"

    @property
    def time_between_frames_ms(self):
        return self._time_between_frames_ms

    @property
    def frames_amount(self):
        return int(self._frames_amount)

    @property
    def video_length(self) -> Tuple[int, int]:
        """
        :return: Tuple of integers. The length of the video, minutes and seconds.
        """
        frames_each_sec = 1000 / self.time_between_frames_ms
        all_seconds = int(self.frames_amount / frames_each_sec)
        minutes = all_seconds // 60
        seconds = all_seconds % 60
        return int(minutes), int(seconds)

    def wait_for_buffer(self):
        while len(self._queue) < self.MAX_FRAMES:
            pass

    def empty(self, frame_location: int):
        self._queue = deque()
        self._frames_got_counter = frame_location
        self._frames_played_counter = frame_location

    def set_resize_scale(self, val: int):
        self.__scale_percent = val
