from sqlalchemy import text

from app.core.config import Settings
from app.core.database import engine


def test_configuration_exposes_cors_origins() -> None:
    settings = Settings(cors_origins="http://localhost:4200, http://localhost:4300")

    assert settings.cors_origin_list == ["http://localhost:4200", "http://localhost:4300"]


def test_sqlite_connection_is_available() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
