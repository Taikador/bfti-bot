from functools import cache
from os import getenv
from types import SimpleNamespace

from dotenv import load_dotenv


class Config(SimpleNamespace):
    """Read only config class loading values from .env and environment"""

    def __init__(self):
        self.token = getenv('BOT_TOKEN', '')
        self.prefix = getenv('BOT_PREFIX', '-')
        self.group = getenv('BOT_GROUP', 'yeet')

        self.iserv_username = getenv('ISERV_USERNAME', '')
        self.iserv_password = getenv('ISERV_PASSWORD', '')

        self.debug = getenv('DEBUG', 'true') != 'false'


load_dotenv()
config = Config()
