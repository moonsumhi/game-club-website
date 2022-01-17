from odmantic import Model
from typing import Optional


class PostModel(Model):
    title: str
    content: str
    createdAt: str
    comments: Optional[str]

    class Config:
        collection = "posts"
