from sqlalchemy import Column, String, Integer, Table, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Schema = declarative_base()


class User(Schema):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    Name =Column(String)
    hashed_password = Column(String)
    email = Column(String)


class Post(Schema):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(primary_key=True)


class Post_to_tag(Schema):
    __tablename__ = "post_to_tag"
    id = Column(Integer, primary_key=True)
    post_id = Column(primary_key=True)
    tag_id = Column(primary_key=True)


class Tag(Schema):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    title = Column(String)