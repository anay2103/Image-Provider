from typing import Any, Dict, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Настройки проекта."""

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_URI: Optional[str]

    @validator('REDIS_URI', pre=True)
    def build_redis_uri(cls, uri, values: Dict[str, Any]) -> str:
        return 'redis://%s:%s' % (values['REDIS_HOST'], values['REDIS_PORT'])

    class Config:
        env_file = '.env'
