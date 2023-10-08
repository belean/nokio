from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base
    # debug: bool
    # project_name: str
    # version: str
    # description: str

    # Database
    # db_async_connection_str: str
    MONGODB_USER: str
    MONGODB_PASSWD: str
    MONGODB_DB: str
