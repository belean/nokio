from pydantic import BaseSettings

class Settings(BaseSettings):
    # Base
    debug: bool
    project_name: str
    version: str
    description: str

    # Database
    db_async_connection_str: str