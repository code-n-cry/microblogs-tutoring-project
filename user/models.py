from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Schema = declarative_base()

class UserModel(Schema):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class User(BaseModel):
    username: str
    email: str


class UserInDB(User):
    hashed_password: str