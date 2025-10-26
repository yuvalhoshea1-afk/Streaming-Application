import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = int(os.environ.get('SERVER_PORT'))
