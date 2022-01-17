from fastapi import APIRouter, Depends
from app.routers.login import templates
from fastapi import Request
from app.models.post import PostModel
from app.models import mongodb
from app.config import PAGES_PER_PAGE
from app.auth.auth_bearer import JWTBearer
from odmantic.query import desc
from typing import List, Dict
from bson import ObjectId
import datetime

router = APIRouter()


@router.get("/post_detail", dependencies=[Depends(JWTBearer())])
async def get_post_detail(request: Request, post_id: str):
    post_id = ObjectId(post_id)
    post = await mongodb.engine.find_one(PostModel, PostModel.id == post_id)
    return templates.TemplateResponse(
        "post_detail.html", {"request": request, "post": post}
    )


@router.get("/post", dependencies=[Depends(JWTBearer())])
def get_board(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})


@router.get("/board", dependencies=[Depends(JWTBearer())])
async def get_board(request: Request, page_num: int = 1):
    page_num = max(1, page_num)

    if page_num % 5 == 1:
        start = page_num
    else:
        start = max(1, 5 * (page_num // 5))

    nums_of_pages = page_num
    for i in range(5):
        if await get_posts(nums_of_pages):
            nums_of_pages += 1
        else:
            break

    if page_num <= nums_of_pages:
        pages = await get_posts(page_num)

    return templates.TemplateResponse(
        "community.html",
        {
            "request": request,
            "start": start,
            "current_page": page_num,
            "pages": pages,
            "nums_of_pages": nums_of_pages,
        },
    )


async def get_posts(page: str) -> List[PostModel]:
    posts = await mongodb.engine.find(
        PostModel,
        sort=desc(PostModel.id),
        skip=(page - 1) * PAGES_PER_PAGE,
        limit=PAGES_PER_PAGE,
    )

    return posts


# 글 생성
@router.post("/post", dependencies=[Depends(JWTBearer())])
async def create_post(request: Request):
    form = await request.form()
    title = form.get("post_title")
    content = form.get("post_content")

    errors = []
    if not title:
        errors.append("Enter valid title")
        return templates.TemplateResponse(
            "post.html", {"request": request, "errors": errors}
        )
    if not content:
        errors.append("Enter valid content")
        return templates.TemplateResponse(
            "post.html", {"request": request, "errors": errors}
        )

    post = PostModel(
        title=title, content=content, createdAt=str(datetime.datetime.now()),
    )

    await mongodb.engine.save(post)

    return await get_board(request)
