from models.db import Base
from settings import get_settings


settings = get_settings()

Base.metadata.create_all(settings.engine)
