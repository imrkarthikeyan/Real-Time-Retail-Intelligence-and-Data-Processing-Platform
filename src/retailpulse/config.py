from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application configuration."""

    postgres_db: str = "retail_db"
    postgres_user: str = "retail"
    postgres_password: str = "retail_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    data_root: Path = Path("data")
    gen_customers: int = 10_000
    gen_products: int = 1_000
    gen_orders: int = 100_000
    spark_master_url: str = "local[*]"
    seaweed_s3_port: int = 8333
    seaweed_access_key: str = "retailpulse"
    seaweed_secret_key: str = "retailpulse_secret"
    seaweed_bucket: str = "retailpulse"
    seaweed_s3_endpoint: str = "http://localhost:8333"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
