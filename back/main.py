from fastapi import FastAPI
from starlette.requests import Request
from back.database import engine
from back.models import Base
from back.handlers.handlers import router
from fastapi.templating import Jinja2Templates

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)

templates = Jinja2Templates(directory="back/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
