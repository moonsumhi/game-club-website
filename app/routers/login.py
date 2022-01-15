from fastapi import Request, HTTPException, Response
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from app.models.user import UserModel
from app.models import mongodb
from app.config import BASE_DIR, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext


templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


class NewUser(BaseModel):
    user_id: str
    name: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


@router.post("/sign_up")
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


@router.get("/login", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
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
            msg = "Login successful"
            response = templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
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
