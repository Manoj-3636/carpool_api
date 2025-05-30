import os
from typing import Annotated

import jwt

from db import db
from fastapi.params import Header, Cookie

from users.exceptions import InvalidToken
from users.models import UserDatabase

ALGORITHM = "HS256"
users_collection = db["users"]
SECRET_KEY = os.getenv("SECRET_KEY")


async def get_current_user(access_token:Annotated[str,Cookie()]):
    token_data = jwt.decode(access_token,SECRET_KEY,algorithms=[ALGORITHM])
    _id = token_data["sub"]
    user_data = await users_collection.find_one({"_id":_id})
    return UserDatabase(**user_data)