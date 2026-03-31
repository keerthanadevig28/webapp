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

    # S3 configuration
    s3_bucket_name: str = ""
    aws_region: str = "us-east-1"

    sns_topic_arn: str = "" 

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
        "env_file_override": False
    }


@lru_cache()
def get_settings():
    return Settings()
