from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "webapp_db"
    db_user: str = "postgres"
    db_password: str = ""
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
