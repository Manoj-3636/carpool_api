from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dependencies import get_current_user
from .exceptions import UserNotFound
from .models import UserDatabase
from db import db

users_collection = db["users"]
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

#Listing current user as a dependency helps enforce security also gives scope to further functionality
# Like is friend etc

async def get_username(_id:str):
    user_db = await users_collection.find_one({"_id":_id})
    return user_db.get("name")
@router.get("/{user_id}")
async def get_user(current_user:Annotated[UserDatabase,Depends(get_current_user)],user_id:str):
    req_user = await users_collection.find_one({"_id" : user_id})
    req_user["id"] = req_user["_id"]
    del req_user["_id"]
    # To send with field name as id and maintain homogeneity throughout the codebase
    if req_user:
        return JSONResponse(
            content ={"user":req_user},
            status_code=200
        )

    else:
        raise UserNotFound(user_id=user_id,detail="The requested user_id was not found")



