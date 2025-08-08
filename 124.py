import session
from models import Student,Author,Book

session.init_db()

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


cursor = next(get_db())
author = cursor.query(Author).order_by(Author.year).all()
for i in author:
    print(i.name,i.year)
    for x in i.books:
        print(x.title)
cursor.commit()
cursor.close()
