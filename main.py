from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'title': 'Главная'})
