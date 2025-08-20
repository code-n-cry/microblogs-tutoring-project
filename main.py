import jwt
from fastapi import FastAPI, Request, Cookie, Depends, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from fastapi.responses import RedirectResponse
from models import User, Post
from user.utils import ALGORITHM, SECRET_KEY, hash_password, verify_password, generate_access_token
import time
import os
import shutil
import session

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
session.init_db()


def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        access_token: str = Cookie('access_token'),
        db: session = Depends(get_db)
):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
    except Exception as e:
        print(e)
        return None
    user = db.query(User).filter_by(email=email).first()
    return user


@app.get('/')
def index(request: Request):
    db = next(get_db())
    current_user = get_current_user(request.cookies.get('access_token'), db=db)
    all_posts = db.query(Post).all()
    return templates.TemplateResponse('index.html',
                                      {'request': request, 'title': 'Главная', 'user': current_user, \
                                       'all_posts': all_posts})


@app.get('/signup')
def signup(request: Request):
    return templates.TemplateResponse('signup.html', {'request': request, 'title': 'Регистрация'})


@app.post('/signup')
def signup(request: Request, username: str = Form(...),
           email: str = Form(...), password: str = Form(...), db: session = Depends(get_db)):
    if len(password) < 5 or not any(i.isalpha() for i in password) or not any(i.isdigit() for i in password):
        return templates.TemplateResponse('signup.html', {
            'request': request,
            'error': 'Пароль должен содержать не менее 5 символов, включая буквы и цифры.'
        })
    is_user_already_exists = db.query(User).filter_by(email=email).first()
    if is_user_already_exists:
        return templates.TemplateResponse('signup.html', {
            'request': request,
            'error': 'Такой пользователь уже есть!'
        })
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
def login_post(request: Request, email: str = Form(...), password: str = Form(...), db: session = Depends(get_db)):
    is_user_already_exists = db.query(User).filter_by(email=email).first()
    if not is_user_already_exists or not verify_password(password, is_user_already_exists.hashed_password):
        return templates.TemplateResponse('login.html',
                                          {'request': request, 'title': 'Вход', 'error': 'Неверный ввод данных'})
    token = generate_access_token(data={'sub': email})
    responce = RedirectResponse(url='/', status_code=302)
    responce.set_cookie(key="access_token", value=token, httponly=True)
    return responce


@app.get('/create_post')
def create_get(request: Request):
    current_user = get_current_user(request.cookies.get('access_token'), db=next(get_db()))
    if current_user is None:
        return RedirectResponse(url='/signup')
    return templates.TemplateResponse('create_post.html', {'request': request, 'title': 'создать пост'})


@app.post('/create_post')
def create_post(request: Request, name: str = Form(...), content: str = Form(...), images: List[UploadFile] = File(...),db: session = Depends(get_db)):
    current_user = get_current_user(request.cookies.get('access_token'), db=db)
    post = Post()
    post.title = name
    post.content = content
    post.author = current_user
    if images:
        if len(images) > 5:
            error = 'Не может быть больше 5 картинок!'
            return templates.TemplateResponse('create_post.html', {'request': request, 'title': 'создать пост', 'error': error})
        if len(images) >= 1 and images[0].filename != '':
            '''path = f'static/media/{current_user.name}_{time.time()}'
            os.makedirs(path, exist_ok=True)
            for image in images:'''

    db.add(post)
    db.commit()
    return RedirectResponse(url='/', status_code=302)


@app.get('/profile')
def profile(request: Request, db: session = Depends(get_db)):
    is_authorized = get_current_user(request.cookies.get('access_token'), db=db)
    if not is_authorized:
        return RedirectResponse(url='/login')
    avatar = None
    if is_authorized.avatar:
        avatar = is_authorized.avatar
    return templates.TemplateResponse('profile.html',
                                      {'request': request, 'user': is_authorized, 'title': 'Ваш профиль',
                                       'avatar': avatar})


@app.get('/profile/edit')
def profile_edit(request: Request, db: session = Depends(get_db)):
    is_authorized = get_current_user(request.cookies.get('access_token'), db=db)
    if not is_authorized:
        return RedirectResponse(url='/login')
    return templates.TemplateResponse('profile_edit.html',
                                      {'request': request, 'user': is_authorized, 'title': 'Изменение профиля'})


@app.post('/profile/edit')
def profile_edit(request: Request, name: str = Form(...), avatar: UploadFile = File(...),
                 db: session = Depends(get_db)):
    is_authorized = get_current_user(request.cookies.get('access_token'), db=db)
    if not is_authorized:
        return RedirectResponse(url='/login', status_code=302)
    if name != is_authorized.name:
        is_authorized.name = name
    if avatar:
        try:
            path = f'static/media/{is_authorized.name}_{time.time()}'
            os.makedirs(path, exist_ok=True)
            with open(path + '/' + avatar.filename, "wb") as file_path:
                shutil.copyfileobj(avatar.file, file_path)
            is_authorized.avatar = path[7:] + '/' + avatar.filename
        except Exception as e:
            pass
    db.add(is_authorized)
    db.commit()
    return RedirectResponse(url='/profile', status_code=302)


@app.get('/users/{user_id}')
def get_user(request: Request, user_id: int, db: session = Depends(get_db)):
    need_user = db.query(User).get(user_id)
    error = None
    if need_user is None:
        error = True
    return templates.TemplateResponse('user_detail.html',
                                      {'request': request, 'user': need_user, 'error': error})


@app.get('/posts/{post_id}')
def get_posts(request:Request,post_id: int, db: session = Depends(get_db)):
    need_post = db.query(Post).get(post_id)
    error = None
    if need_post is None:
        error = True
    return templates.TemplateResponse('post_detail.html',
                                      {'request': request, 'post': need_post,'error': error})
