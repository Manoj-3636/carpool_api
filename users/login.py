import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Depends,Response
from fastapi.params import Cookie
from fastapi.encoders import jsonable_encoder
from google.auth.transport import requests as grequests
from google.oauth2 import id_token as google_id_token
from starlette.responses import JSONResponse

from db import db
from users.exceptions import InvalidToken
from users.models import UserDatabase, UserReq, ReceivedToken

load_dotenv(override=True)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
users_collection = db["users"]
ALGORITHM = "HS256"
router = APIRouter(
    prefix="/login",
    tags = ["users"],
)

def create_access_token(data:dict,expires_delta:timedelta = timedelta(weeks=1)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def user_from_id(received_token:ReceivedToken):
    try:
        id_info = google_id_token.verify_oauth2_token(received_token.id_token, grequests.Request(), GOOGLE_CLIENT_ID)
        user: UserReq = UserReq(**id_info)
        return user

    except ValueError:
        raise InvalidToken(received_token.id_token,"Google Authentication Failed")


async def check_add_and_return(user:UserReq):
    # returns if the user already exists
    found = await users_collection.find_one({"_id" : user.email[1:9]})
    if found:
        return UserDatabase(**found)
    userdb = UserDatabase(email=user.email,name=user.name,_id=user.email[1:9])
    await users_collection.insert_one(jsonable_encoder(userdb))
    return userdb


def is_token_valid(access_token):
    print("Checking",access_token)
    if not access_token:
        return False

    try:
        _id = jwt.decode(access_token,SECRET_KEY,algorithms=[ALGORITHM])
        return True
    except ValueError:
        return False



@router.post("/token")
async def login_handler(user:Annotated[UserReq,Depends(user_from_id)]):
    print(user.name,user.email)
    userdb = await check_add_and_return(user)
    jwt = create_access_token({"sub":userdb.id})
    response = JSONResponse(content = "Success")
    response.set_cookie(key="access_token",value=jwt,httponly=True)
    return response

@router.get("/status")
async def login_status_handler(access_token:Annotated[str,Cookie()] = None):
    if is_token_valid(access_token):
        return JSONResponse(
            content={"logged_in":True},
            status_code = 200
        )

    else:
        return JSONResponse(
            content={"logged_in":False},
            status_code=200,
        )


