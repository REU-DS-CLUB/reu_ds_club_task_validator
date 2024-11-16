from fastapi import FastAPI
from starlette.requests import Request
from back.database import engine
from back.models import Base
from fastapi.templating import Jinja2Templates
from back.handlers import router as handlers_router

app = FastAPI()

app.include_router(handlers_router)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="back/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
