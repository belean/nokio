from os import getenv
from dotenv import load_dotenv

from nokio.core.config import Settings

load_dotenv(getenv())

settings=Settings()