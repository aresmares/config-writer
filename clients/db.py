from typing import Annotated, Callable

from fastapi import Depends, Request
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, Session

from clients.definition import Client
from models.db import Config


class DB(Client):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db: Session | None = None  # Initialize db as None

    def start(self):
        if self.db is None:
            self.db = self.SessionLocal()

    def get(self, key: str) -> Config | None:
        return self.db.query(Config).filter(Config.key == key).first()

    def get_all(self) -> list[Config]:
        return self.db.query(Config).all()

    def create(self, key: str, value: str, type: str) -> Config:
        db_config = Config(key=key, value=value, type=type)
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def update(self, key: str, value: str) -> Config:
        db_config = self.get(key)
        db_config.value = value
        self.db.commit()
        self.db.refresh(db_config)
        return db_config

    def delete(self, key: str) -> None:
        db_config = self.get(key)
        if not db_config:
            return None
        self.db.delete(db_config)
        self.db.commit()
        return db_config

    def close(self):
        if self.db:
            self.db.close()
            self.db = None  # Reset db to None after closing


def get_client(name: str) -> Callable[[Request], Client]:
    def service(request: Request) -> Client:
        return getattr(request.app.state, name)

    return service


DBDependency = Annotated[DB, Depends(get_client("db"))]
