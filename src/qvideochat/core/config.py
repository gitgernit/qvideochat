import pathlib

import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=pathlib.Path(__file__).parent.parent.parent.parent / '.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    GRPC_SERVER_HOST: str = pydantic.fields.Field(default='127.0.0.1')
    GRPC_SERVER_PORT: str = pydantic.fields.Field(default='8080')


config = Config()
