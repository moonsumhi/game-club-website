from odmantic import Model
from typing import List, Dict


class UserModel(Model):
    user_id: str
    name: str
    password: str

    class Config:
        collection = "users"
