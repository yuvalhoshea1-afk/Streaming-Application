import os.path
import sys
import time
from typing import Dict
import cv2
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from client import Client
import image_functions


IMAGES_IN_LINE = 3
TITLE_IMAGE = "title.jpg"


def get_title_qimage() -> QImage:
    # get the path of the title image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, TITLE_IMAGE)
    # get the image and convert to QImage
    img_arr = cv2.imread(image_path)
    q_img = image_functions.convert_numpy_array_to_qimage(img_arr)
    return q_img


class VideoDialog(QDialog):
    """
    Dialog that let the user choose which video he wants to watch.
    """
    def __init__(self, videos: Dict[str, str]):
        """
        :param videos: list of string. List of all the videos.
        """
        super(VideoDialog, self).__init__()
        self.setGeometry(0, 0, 500, 500)
        self.__video_name = ""
        self.layout = QVBoxLayout(self)
        # Title image
        title_image = QLabel()
        title_image.setPixmap(QPixmap(get_title_qimage()))
        self.layout.addWidget(title_image)

        last_row_layout = None
        # add videos buttons to the dialog
        for (index, video) in enumerate(videos.keys()):
            img_arr = image_functions.resize_image_to_specific_height(videos[video], wanted_height=250)
            q_img = image_functions.convert_numpy_array_to_qimage(img_arr)
            image = ImageButton(self, video, q_img)

            row, col = index // IMAGES_IN_LINE + 1, index % IMAGES_IN_LINE
            if col == 0:
                # create new row
                row_layout = QHBoxLayout()
                self.layout.addLayout(row_layout)
                last_row_layout = row_layout
            else:
                row_layout = last_row_layout

            row_layout.addWidget(image)

        for _ in range(0, IMAGES_IN_LINE - last_row_layout.count()):
            last_row_layout.addWidget(QLabel())

        self.style()
        self.show()

        if self.exec_() == QDialog.Rejected:
            sys.exit()

    def video_name(self):
        return self.__video_name

    def set_selected_video(self, video_name: str):
        self.__video_name = video_name

    def style(self):
        """
        Style the dialog
        """
        style = """
                QDialog{
                    background-color: white;
                }
                """

        self.setStyleSheet(style)


class ImageButton(QLabel):
    """
    Button that which is an image. Used in VideoDialog
    """

    def __init__(self, dialog: VideoDialog, video_name: str, q_image: QImage, *args, **kwargs):
        super(ImageButton, self).__init__(*args, **kwargs)
        self.__dialog = dialog
        self.__video_name = video_name
        pixmap = QPixmap(q_image)
        self.setPixmap(pixmap)
        self.style_image()

    def style_image(self):
        style = """
                QLabel {
                    margin: 10px 10px;
                    padding: 10px 10px;
                }
                QLabel:hover {
                    background-color: rgb(196, 196, 196);
                }
                """

        self.setStyleSheet(style)

    def mousePressEvent(self, ev) -> None:
        """
        When button pressed we close the dialog by accepting it.
        """
        super().mousePressEvent(ev)
        self.__dialog.set_selected_video(self.__video_name)
        self.__dialog.accept()


class UsernamePasswordDialog(QDialog):
    """
    A class that LoginDialog and RegisterDialog inherited from it.
    """
    def __init__(self, title_name: str):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.title = QLabel(title_name)
        self.layout.addWidget(self.title)

        hbox_layout1 = QHBoxLayout()
        self.user_label = QLabel('Username: ')
        self.user_text_box = QLineEdit()
        hbox_layout1.addWidget(self.user_label)
        hbox_layout1.addWidget(self.user_text_box)
        self.layout.addLayout(hbox_layout1)

        hbox_layout2 = QHBoxLayout()
        self.password_label = QLabel('Password: ')
        self.password_text_box = QLineEdit()
        self.password_text_box.setEchoMode(QLineEdit.Password)
        hbox_layout2.addWidget(self.password_label)
        hbox_layout2.addWidget(self.password_text_box)
        self.layout.addLayout(hbox_layout2)

        hbox_layout3 = QHBoxLayout()
        self.button = QPushButton('Submit')
        self.button.clicked.connect(self.on_submit)
        hbox_layout3.addWidget(self.button)
        self.layout.addLayout(hbox_layout3)

    def show_dialog(self):
        self.show()
        if self.exec_() == QDialog.Rejected:
            sys.exit()

    def on_submit(self):
        """
        Executes when clicking the submit button.
        """
        pass

    def style(self):
        style = "margin: 10px 10px; padding: 10px 10px;"

        self.user_label.setStyleSheet(style)
        self.user_text_box.setStyleSheet(style)
        self.password_label.setStyleSheet(style)
        self.password_text_box.setStyleSheet(style)
        self.button.setStyleSheet(style)

        self.title.setStyleSheet("font-weight: bold;")


class LoginDialog(UsernamePasswordDialog):
    def __init__(self, client: Client):
        super().__init__('Login: ')
        self.logged_in = False
        self.client = client

    def on_submit(self):
        username = self.user_text_box.text()
        password = self.password_text_box.text()
        if len(password) == 0 or len(username) == 0:  # make sure we don't get an empty string
            return
        # login to server
        self.client.login(username, password)
        while self.client.logged_in is None:
            time.sleep(0.01)
        # did we login?
        logged = self.client.logged_in
        if logged:
            self.logged_in = True
            self.accept()
        else:
            QMessageBox.about(QWidget(), "Something went wrong",
                              "Username/password is wrong.")
            self.client.logged_in = None


class RegisterDialog(UsernamePasswordDialog):
    def __init__(self, client: Client):
        super().__init__('Register: ')
        self.client = client

    def on_submit(self):
        username = self.user_text_box.text()
        password = self.password_text_box.text()
        if len(password) == 0 or len(username) == 0:  # make sure we don't get an empty string
            return

        self.client.create_user(username, password)
        while self.client.created_user is None:
            time.sleep(0.01)
        created = self.client.created_user
        if created:
            self.accept()
        else:
            QMessageBox.about(QWidget(), "Failed", "User is already exists. Please use another username.")
            self.client.created_user = None


class HomePageDialog(QDialog):

    def __init__(self, client: Client):
        super().__init__()
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.client = client

        self.layout = QHBoxLayout(self)

        button1 = QPushButton('register')
        button1.clicked.connect(self.connect_register_dialog)
        self.layout.addWidget(button1)

        button2 = QPushButton('login')
        button2.clicked.connect(self.connect_login_dialog)
        self.layout.addWidget(button2)
        self.show()
        if self.exec_() == QDialog.Rejected:
            sys.exit()

    def connect_login_dialog(self):
        login = LoginDialog(self.client)
        login.show_dialog()
        if login.logged_in:
            self.accept()

    def connect_register_dialog(self):
        register = RegisterDialog(self.client)
        register.show_dialog()
        QMessageBox.about(QWidget(), "SUCCESS", "User has been created. Please login.")
