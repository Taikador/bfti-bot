from os import getenv
from types import SimpleNamespace
from typing import List

from dotenv import load_dotenv


class Config(SimpleNamespace):
    """Read only config class loading values from .env and environment"""

    def __init__(self):
        self.token: str = getenv('BOT_TOKEN', '')
        self.prefix: str = getenv('BOT_PREFIX', '-')
        self.moderation_roles: List[int] = [
            int(role_id) for role_id in getenv('MODERATION_ROLES', 'yeet').split(',')
        ]
        self.guild_id: int = int(getenv('GUILD_ID', None))
        self.channel_id: int = int(getenv('CHANNEL_ID', None))

        self.iserv_username: str = getenv('ISERV_USERNAME', '')
        self.iserv_password: str = getenv('ISERV_PASSWORD', '')

        self.debug: bool = getenv('DEBUG', 'true') != 'false'


load_dotenv()
config = Config()
