import os
import pprint
from typing import Annotated
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as grequests
from fastapi import HTTPException, Depends
from fastapi import APIRouter
from pydantic import BaseModel

from db import db
from dotenv import load_dotenv

from users.exceptions import InvalidToken

load_dotenv(override=True)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
users_collection = db["users"]



router = APIRouter(
    prefix="/login",
    tags = ["users"],
)

class UserLogin(BaseModel):
    email:str
    given_name:str

class ReceivedToken(BaseModel):
    id_token:str

#     This class wil help eventually parsing more information from the request

async def user_from_id(received_token:ReceivedToken):
    try:
        id_info = google_id_token.verify_oauth2_token(received_token.id_token, grequests.Request(), GOOGLE_CLIENT_ID)
        user: UserLogin = UserLogin(**id_info)
        return user

    except ValueError:
        raise InvalidToken(received_token.id_token,"Google Authentication Failed")



@router.post("/token")
async def login_handler(user:Annotated[UserLogin,Depends(user_from_id)]):
    print(user.email)




