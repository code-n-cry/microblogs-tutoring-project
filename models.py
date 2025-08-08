from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Schema = declarative_base()

post_to_tag = Table(
    "post_to_tag", Schema.metadata,
    Column("tag_id", Integer, ForeignKey("tags.id")),
    Column("post_id", Integer, ForeignKey("posts.id")),
)


class User(Schema):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    Name =Column(String)
    hashed_password = Column(String)
    email = Column(String)
    posts = relationship("Post", back_populates="author")


class Post(Schema):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(ForeignKey("user.id"))
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", back_populates="posts")


class Post_to_tag(Schema):
    __tablename__ = "post_to_tag"
    id = Column(Integer, primary_key=True)
    post_id = Column(primary_key=True)
    tag_id = Column(primary_key=True)


class Tag(Schema):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    posts = relationship("Post", back_populates="tags")
