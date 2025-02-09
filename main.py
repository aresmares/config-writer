from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from clients.db import DBDependency
from models.db import Config
from models.requests import ConfigCreate, ConfigUpdate, ConfigResponse

from settings import get_settings
import services as my_services

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = my_services.create_services()
    for key, service in services.items():
        service.start()
        setattr(app.state, key, service)
    try:
        yield
    finally:
        for key, service in services.items():
            service.close()


# FastAPI app initialization
app = FastAPI(
    title="Config API",
    lifespan=lifespan,
    version="0.1.0",
    description="A simple API to manage configurations",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only; restrict this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/configs", response_model=list[ConfigResponse])
async def read_configs(db: DBDependency) -> list[Config]:
    configs = db.get_all()
    return configs


@app.get("/configs/{key}", response_model=ConfigResponse)
def read_config(key: str, db: DBDependency):
    config = db.get(key)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@app.post("/configs", response_model=ConfigResponse)
def create_config(config: ConfigCreate, db: DBDependency) -> Config:
    db_config = db.get(config.key)
    if db_config:
        raise HTTPException(status_code=400, detail="Config already exists")

    updated = db.create(key=config.key, value=config.value, type=config.type)
    return updated


@app.put("/configs/{key}", response_model=ConfigResponse)
def update_config(key: str, config_update: ConfigUpdate, db: DBDependency) -> Config:
    config = db.get(key)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")
    config = db.update(key, config_update.value)
    return config


@app.delete("/configs/{key}", response_model=ConfigResponse)
def delete_config(key: str, db: DBDependency) -> Config:
    config = db.delete(key)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")

    return config


if __name__ == "__main__":
    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")
    uvicorn.run(app, host=settings.host, port=settings.port)
