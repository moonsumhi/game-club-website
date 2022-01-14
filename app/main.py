from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from app.models.user import UserModel
from app.models import mongodb
from app.config import BASE_DIR, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class NewUser(BaseModel):
    user_id: str
    name: str
    password: str


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


@app.post("/sign_up")
async def sign_up(new_user: NewUser):
    user = UserModel(
        user_id=new_user.user_id,
        name=new_user.name,
        password=get_password_hash(new_user.password),
    )
    if await mongodb.engine.find_one(UserModel, UserModel.user_id == user.user_id):
        raise HTTPException(status_code=400, detail="ID duplicated")
    else:
        await mongodb.engine.save(user)
        return {"message": "New user created successfully"}


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(user_id, password):
    user = await mongodb.engine.find_one(UserModel, UserModel.user_id == user_id)

    if user:
        password_check = pwd_context.verify(password, user.password)

        return password_check
    else:
        return False


from datetime import timedelta, datetime
from jose import jwt


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = form_data.username
    password = form_data.password

    if await authenticate_user(user_id, password):
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect id or password")


@app.get("/")
def root(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.on_event("startup")
async def on_app_start():
    await mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    await mongodb.close()
