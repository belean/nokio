from os import getenv
from dotenv import load_dotenv, find_dotenv

from nokio.core.config import Settings
from nokio.core.utils import open_jsonc, chunk


# load_dotenv(getenv())
load_dotenv(find_dotenv())

settings = Settings()
