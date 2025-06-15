from typing import Final

from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    PROJECT_NAME: str = 'caipyra-ledger'
    PROJECT_DESCRIPTION: str = 'Ledger'
    PROJECT_VERSION: str = '0.0.1'
    DEBUG: bool = True

    DB_USER: str = 'user'
    DB_PASSWORD: str = 'password'
    DB_HOST: str = 'localhost'
    DB_PORT: str = '5432'
    DB_NAME: str = 'ledger'
    SQLALCHEMY_ECHO: bool = True

    @property
    def SQLALCHEMY_DB_URI(self) -> str:
        return 'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME,
        )

    class Config:
        case_sensitive = True


settings: Final = _Settings()
