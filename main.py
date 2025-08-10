import jwt
from fastapi import FastAPI, Request, Cookie, Depends, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse


from models import User
from user.utils import ALGORITHM, SECRET_KEY, hash_password,verify_password,generate_access_token
import session

app = FastAPI()
templates = Jinja2Templates(directory="templates")
session.init_db()


def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        access_token: str = Cookie(None),
        db: session = Depends(get_db)
):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, secret_key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
    except Exception as e:
        return None
    user = db.query(User).filter_by(email=email).first()
    return user


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'title': 'Главная'})


@app.get('/signup')
def signup(request: Request):
    return templates.TemplateResponse('signup.html', {'request': request, 'title': 'Регистрация'})


@app.post('/signup')
def signup(request: Request, username: str = Form(...),
           email: str = Form(...), password: str = Form(...), db: session = Depends(get_db)):
    is_user_already_exists = db.query(User).filter_by(email=email).first()
    print(is_user_already_exists)
    if is_user_already_exists:
        return templates.TemplateResponse('signup.html', {'request': request,
                                                          'error': 'Такой пользователь уже есть!'})
    user = User()
    user.email = email
    user.name = username
    user.hashed_password = hash_password(password)
    db.add(user)
    db.commit()
    return RedirectResponse(url='/login')


@app.get('/login')
def login_get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request, 'title': 'Вход'})


@app.post('/login')
def login_post(request: Request,email: str = Form(...),password: str = Form(...), db: session = Depends(get_db)):
    is_user_already_exists = db.query(User).filter_by(email=email).first()
    if  not is_user_already_exists or verify_password(password,is_user_already_exists.hashed_password):
        return {'error':'Неверный ввод данных'}
    token = generate_access_token(data={'username': is_user_already_exists.name,'email': email})
    responce = RedirectResponse(url='/')
    responce.set_cookie(key="access_token",value=token,httponly=True)
    return responce