from quasiqueue import Settings as QuasiQueueSettings

from .db import DatabaseSettings


class Settings(QuasiQueueSettings, DatabaseSettings):
    project_name: str = "koha_framework_tools"
    debug: bool = False
