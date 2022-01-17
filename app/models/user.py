from odmantic import Model


class UserModel(Model):
    user_id: str
    name: str
    password: str

    class Config:
        collection = "users"
