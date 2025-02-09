# Updated Config model with a type field.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Create tables
class Config(Base):
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    type = Column(String, nullable=False, default="string")  # "string" or "boolean"

    def __repr__(self):
        return f"<Config(key='{self.key}', value='{self.value}', type='{self.type}')>"

