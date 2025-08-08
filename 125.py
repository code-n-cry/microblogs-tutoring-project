import session
from models import Student,Subject,Grade
import random

session.init_db()

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


cursor = next(get_db())