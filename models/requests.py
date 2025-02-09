# Pydantic models
from pydantic import BaseModel


class ConfigCreate(BaseModel):
    key: str
    value: str
    type: str  # Expected to be either "string" or "boolean"


class ConfigUpdate(BaseModel):
    value: str


class ConfigResponse(BaseModel):
    key: str
    value: str
    type: str

    class Config:
        orm_mode = True
