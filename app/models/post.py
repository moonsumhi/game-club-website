from odmantic import Model
from typing import Optional, List


class PostModel(Model):
    title: str
    content: str
    createdAt: str
    comments: Optional[List[str]]

    class Config:
        collection = "posts"
