from typing import Literal

from clients.db import DB
from clients.definition import Client
from settings import get_settings

settings = get_settings()

Services = Literal["db"]

services: dict[Services, Client] = {
    "db": DB(
        engine=settings.engine,
    ),
}


def create_services() -> dict[Services, Client]:
    return services
