import os
from typing import Annotated

import jwt

from db import db
from fastapi.params import Header, Cookie

from users.models import UserDatabase

ALGORITHM = "HS256"
users_collection = db["users"]
SECRET_KEY = "9f59d7b47bb6ec95dac2ce1b5f1813d00daa76832cf2171944cc2d4f9a85fdf4"


async def get_current_user(access_token:Annotated[str,Cookie()]):
    token_data = jwt.decode(access_token,SECRET_KEY,algorithms=[ALGORITHM])
    _id = token_data["sub"]
    user_data = await users_collection.find_one({"_id":_id})
    return UserDatabase(**user_data)