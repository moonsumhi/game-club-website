from fastapi import Request, Response
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from app.models.user import UserModel
from app.models import mongodb
from app.config import BASE_DIR, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
import time


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}


def get_password_hash(password: str):
    return pwd_context.hash(password)


@router.get("/register")
async def sign_up(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def sign_up(request: Request):
    form = await request.form()
    user_id = form.get("user_id")
    user_name = form.get("user_name")
    password = form.get("password")
    errors = []
    if not user_id:
        errors.append("Enter valid ID")
    if not user_name:
        errors.append("Enter valid name")
    if not password:
        errors.append("Enter valid password")

    user = UserModel(
        user_id=user_id, name=user_name, password=get_password_hash(password),
    )

    try:
        if await mongodb.engine.find_one(UserModel, UserModel.user_id == user.user_id):
            errors.append("ID duplicated")
            return templates.TemplateResponse(
                "register.html", {"request": request, "errors": errors}
            )
        else:
            await mongodb.engine.save(user)
            msg = "Registeration Success"
            return templates.TemplateResponse(
                "register.html", {"request": request, "msg": msg}
            )
    except:
        errors.append("Something wrong")
        return templates.TemplateResponse(
            "register.html", {"request": request, "errors": errors}
        )


async def authenticate_user(user_id, password):
    user = await mongodb.engine.find_one(UserModel, UserModel.user_id == user_id)

    if user:
        password_check = pwd_context.verify(password, user.password)
        return password_check
    else:
        return False


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/")
async def login(response: Response, request: Request):
    form = await request.form()
    user_id = form.get("user_id")
    password = form.get("password")
    errors = []
    if not user_id:
        errors.append("Enter valid ID")
    if not password:
        errors.append("Enter valid password")
    try:
        if await authenticate_user(user_id, password):
            access_token = create_access_token(
                data={"sub": user_id}, expires_delta=timedelta(minutes=30)
            )
            response = templates.TemplateResponse("index.html", {"request": request})
            # response.headers["Authorization"] = f"Bearer {access_token}"
            response.set_cookie(
                key="access_token", value=f"Bearer {access_token}", httponly=True
            )
            return response
        else:
            errors.append("Wrong ID or Password")
            return templates.TemplateResponse(
                "login.html", {"request": request, "errors": errors}
            )
    except:
        errors.append("Something wrong")
        return templates.TemplateResponse(
            "login.html", {"request": request, "errors": errors}
        )
