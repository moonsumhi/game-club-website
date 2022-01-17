from fastapi import APIRouter, Depends
from app.routers.login import templates
from app.auth.auth_bearer import JWTBearer
from fastapi import Request


router = APIRouter()


@router.get("/index", dependencies=[Depends(JWTBearer())])
async def base(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
