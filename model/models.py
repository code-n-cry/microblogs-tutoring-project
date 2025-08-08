from sqlalchemy import Column, String, Integer, Table, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Schema = declarative_base()

student_course = Table(
    'student_course', Schema.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)


class Student(Schema):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    grade = Column(Integer)
    courses = relationship('Course', secondary=student_course, back_populates='students')


class Course(Schema):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    students = relationship('Student', secondary=student_course, back_populates='courses')


class Author(Schema):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    books = relationship('Book', back_populates='author')


class Book(Schema):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship('Author', back_populates='books')


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
