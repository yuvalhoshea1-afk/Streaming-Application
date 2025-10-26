import threading
import time
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QSlider, QWidget
from client import Client
from videoplayer import VideoPlayer
import image_functions


PAUSE = "PAUSE"
START = "START"


def format_time(minutes: int, seconds: int) -> str:
    """
    :param minutes: int
    :param seconds: int
    :return: return formatted string at format "[minutes]:[seconds]"
    """
    min_str, sec_str = str(minutes), str(seconds)
    min_str = min_str.zfill(2)
    sec_str = sec_str.zfill(2)
    return f"{min_str}:{sec_str}"


class AskingForFrameThread(threading.Thread):

    def __init__(self, client: Client, video_player: VideoPlayer, vid_name: str):
        super(AskingForFrameThread, self).__init__()
        # Make the thread under the control of the main thread.
        # Therefore it will be stopped when the main thread will end.
        self.daemon = True
        self.client = client
        self.video_player = video_player
        self.vid_name = vid_name
        #
        self.__paused = False
        self.__alive = True

    def run(self) -> None:
        """
        This function executes when you starting the thread.
        The functions ask frames from the server
        """
        while self.__alive:
            if self.__paused:
                continue

            if self.video_player.can_add_frame() and self.client.can_request_frame():
                self.client.ask_for_frame(self.vid_name)

            # Wait a little
            time.sleep(0.001)

    def pause(self) -> None:
        """
        Pausing the request asking
        :return:
        """
        self.__paused = True

    def unpause(self):
        """
        Unpausing the request asking
        :return:
        """
        self.__paused = False

    def kill(self):
        """
        Kill the thread (Stopping the loop in the thread)
        """
        self.__alive = False


class FrameSlider(QSlider):

    def __init__(self, father_widget, video_player: VideoPlayer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__father_widget = father_widget
        self.__video_player = video_player

    def mousePressEvent(self, ev) -> None:
        """
        Executes when the user pressing the slider with the mouse.
        When pressing the slider we pause the streaming because we want
        to wait for the user to change the time of the video.
        """
        super().mousePressEvent(ev)
        self.__father_widget.stream = False

    def mouseReleaseEvent(self, ev) -> None:
        """
        Executes when releasing the mouse from the slider. Get the location that the user pressed
        and then calculate the selected frame on that location. Than changing the frame to the selected
        frame on the main window.
        """
        super().mouseReleaseEvent(ev)
        # calculate the frame from the location on the slider
        new_pos = self.value()
        selected_frame = round(new_pos * self.__video_player.frames_amount / self.width())
        self.__father_widget.change_video_frame(selected_frame)


class Window(QWidget):

    def __init__(self, client: Client, video_player: VideoPlayer, title: str, asking_frame_thread: AskingForFrameThread):
        super().__init__()
        self.__closed = False

        self.client = client
        self.video_player = video_player
        self.asking_for_frame_thread = asking_frame_thread
        self.setWindowTitle(title)

        self.setGeometry(60, 60, 600, 6000)
        # frames generator
        self.frames = video_player.get_frames()
        # timer for changing the frame
        self.timer = QTimer()
        self.delay = video_player.time_between_frames_ms
        self.current_second = 0.0
        self.last_second = 0.0
        # img label, where the image will be shown
        self.img_label = QLabel(self)
        # buttons
        self.pause_start_button = QPushButton(START, self)
        # we streaming?
        self.stream = True
        # slider
        self.frame_slider = FrameSlider(self, video_player, Qt.Horizontal, self)
        self.slider_last_value = 0
        # label for time
        self.video_length_label = QLabel(self)
        self.current_time_label = QLabel(self)
        #
        self.resize_slider = QSlider(Qt.Horizontal, self)

        self.resize_text_label = QLabel(self)

        self.current_frame = 0

        self.initUI()

    def initUI(self):
        # slider "things" frames_amount
        self.frame_slider.setFocusPolicy(Qt.NoFocus)
        self.frame_slider.setFixedWidth(self.window().width())

        # what happens when you click "pause"/"start"
        self.pause_start_button.clicked.connect(self.pause_start_click)
        # set labels text
        self.video_length_label.setText(format_time(*self.video_player.video_length))
        self.current_time_label.setText(format_time(0, 0))

        self.resize_slider.setFocusPolicy(Qt.NoFocus)
        self.resize_slider.setFixedWidth(100)
        self.resize_slider.valueChanged.connect(self.resize_frame)
        self.resize_slider.setRange(25, 115)
        self.resize_slider.setValue(100)

        self.resize_text_label.setText("Resize video: ")

        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(self.delay)

    def show_img(self, img_array: np.array):
        """
        :param img_array: numpy array.
        :return: None. Show the image in the window
        """
        qimg = image_functions.convert_numpy_array_to_qimage(img_array)
        pixmap = QPixmap(qimg)

        width, height = pixmap.width(), pixmap.height()
        self.img_label.resize(width, height)
        self.resize(width, height + 100)

        self.pause_start_button.move(0, height + 10)
        y = self.pause_start_button.height() + height + 30

        slider_width = width - 175
        self.frame_slider.setFixedWidth(slider_width)
        self.frame_slider.setRange(1, width - 175)
        self.frame_slider.move(80, y)

        self.resize_text_label.move(self.pause_start_button.x() + self.pause_start_button.width() + 20,
                                    self.pause_start_button.y())

        self.resize_slider.move(self.resize_text_label.x() + self.resize_text_label.width() + 20,
                                self.pause_start_button.y())

        self.current_time_label.move(self.frame_slider.x() - 60, y)
        self.video_length_label.move(self.frame_slider.x() + self.frame_slider.width() + 30, y)
        self.img_label.setPixmap(pixmap)

    def timerEvent(self, e=None) -> None:
        """
        :param e: not used
        :return: None. This function executed every n ms. Get the next frame and then show it on the gui.
        In addition it changes the slider position according to the frame.
        """
        try:
            if not self.stream:
                return

            img = next(self.frames)
            self.show_img(img)
            self.current_frame += 1
            # change slider position
            self.change_slider_position()

            # update video timer labels
            self.current_second += self.video_player.time_between_frames_ms / 1000
            if int(self.last_second) != int(self.current_second):
                minutes = int(self.current_second // 60)
                sec = int(self.current_second % 60)
                self.current_time_label.setText(format_time(minutes, sec))
                # get rid from 1.000201 -> 1.0
                self.current_second = float(int(self.current_second))
                self.last_second = int(self.current_second)

        except StopIteration:
            self.end()
            self.timer.stop()
            return

    def pause_start_click(self):
        """
        This function execute when the user press the "pause" / "start" button.
        :return: None
        """
        button_state = self.pause_start_button.text()

        if button_state == PAUSE:
            self.pause_start_button.setText(START)
        else:
            self.pause_start_button.setText(PAUSE)

        self.stream = not self.stream

    def closeEvent(self, event) -> None:
        """
        :param event: event
        :return: None. Execute before closing
        """
        super().closeEvent(event)
        self.__closed = True

    @property
    def seconds_in_video(self):
        min_in_videos, sec = self.video_player.video_length
        return min_in_videos * 60 + sec

    def end(self):
        """
        :return: None. Execute when the video ends.
        """
        self.img_label.setText("End of the selectd video !\n"
                               "Go back to the menu if you would like to\n"
                               "to see another video or this video again.")

    def change_video_frame(self, new_frame_location: int):
        self.stream = False
        self.asking_for_frame_thread.pause()
        self.client.ask_for_new_location(self.windowTitle(), new_frame_location)
        while not self.client.server_ended_changing_video_position:
            pass
        self.client.server_ended_changing_video_position = False
        self.video_player.empty(new_frame_location)
        self.asking_for_frame_thread.unpause()
        self.current_frame = new_frame_location
        self.current_second = round(self.current_frame / self.video_player.time_between_frames_ms)
        self.stream = True

    def change_slider_position(self):
        self.slider_last_value = self.frame_slider.value()
        ratio = self.frame_slider.width() / self.video_player.frames_amount
        new_position = int(ratio * self.current_frame)
        self.frame_slider.setValue(new_position)

    def resize_frame(self):
        self.video_player.set_resize_scale(self.resize_slider.value())

    def closed_window(self):
        return self.__closed
