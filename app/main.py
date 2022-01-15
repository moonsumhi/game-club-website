from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from app.routers import login
from app.models.user import UserModel
from app.models import mongodb
from app.config import BASE_DIR, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


desc = """
This is the game-club website project 
"""

app = FastAPI(
    title="Game Club Website",
    version=0.8,
    description=desc,
    contact={"name": "Moonsum", "email": "moonsumhi@gmail.com"},
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(login.router)


@app.on_event("startup")
async def on_app_start():
    await mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    await mongodb.close()
