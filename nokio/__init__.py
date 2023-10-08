from os import getenv
from dotenv import load_dotenv, find_dotenv

from nokio.core.config import Settings

# load_dotenv(getenv())
load_dotenv(find_dotenv())

settings = Settings()
