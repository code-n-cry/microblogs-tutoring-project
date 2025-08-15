import jwt
from fastapi import FastAPI, Request, Cookie, Depends, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from models import User,Post
from user.utils import ALGORITHM, SECRET_KEY, hash_password, verify_password, generate_access_token
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
    current_user = get_current_user(request.cookies.get('access_token'), db=next(get_db()))
    return templates.TemplateResponse('index.html', {'request': request, 'title': 'Главная', 'user': current_user})


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
def create_get(request:Request):
    current_user = get_current_user(request.cookies.get('access_token'), db=next(get_db()))
    if current_user == None:
        return RedirectResponse(url='/signup')
    return templates.TemplateResponse('create_post.html',{'request': request,'title': 'создать пост'})


@app.post('/create_post')
def create_post(request:Request,name: str = Form(...), content: str = Form(...),db: session = Depends(get_db)):
    current_user = get_current_user(request.cookies.get('access_token'), db=next(get_db()))
    post = Post()
    post.title = name
    post.content = content
    post.author = current_user
    
    db.add(post)
    db.commit()
    return RedirectResponse(url='/')
     


@app.get('/profile')
def profile(request: Request):
    pass