from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db import db
from users.models import UserDatabase
from users.login import create_access_token

users_collection = db['users']
router = APIRouter(
    prefix="/impersonate",
    tags = ["development"]
)

@router.get("/{user_id}")
async def impersonation_handler(user_id:str):
    user_db = UserDatabase(**(await users_collection.find_one({"_id":user_id})))
    jwt = create_access_token({"sub":user_db.id})
    response = JSONResponse(content={"user": jsonable_encoder(user_db, by_alias=False)})
    response.set_cookie(key="access_token", value=jwt, httponly=True,secure=True,samesite="none")
    return response

