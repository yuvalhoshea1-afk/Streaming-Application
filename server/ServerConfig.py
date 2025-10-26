import logging
import os
from typing import Tuple, List
from dotenv import load_dotenv


# create the logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


IP = os.environ.get("IP")
PORT = int(os.environ.get("PORT"))
MAX_LISTENERS = 10
SERVER_TIMEOUT = 10
VIDEOS_DIR_PATH = os.path.join(os.path.dirname(__file__), "videos")


def all_videos() -> List[str]:
    """
    :return: all the videos available
    """
    files_and_sub_dirs = os.listdir(VIDEOS_DIR_PATH)
    files = filter(lambda potential_dir:
                   os.path.isdir(os.path.join(VIDEOS_DIR_PATH, potential_dir)),
                   files_and_sub_dirs)
    return list(files)


def get_video_and_thumbnail_path(video_dir: str) -> Tuple[str, str]:
    """
    :param video_dir: the video dir
    :return: the path to the video and the path to the video thumbnail
    """
    video_dir = os.path.join(VIDEOS_DIR_PATH, video_dir)
    video_type_file = os.path.join(video_dir, "video_type.txt")
    with open(video_type_file, "r") as file:
        video_extension = file.read()

    vid = f"video.{video_extension}"
    video_path = os.path.join(video_dir, vid)
    thumbnail_path = os.path.join(video_dir, "img.jpg")

    return video_path, thumbnail_path


ALL_VIDEOS_DIRECTORIES = all_videos()

