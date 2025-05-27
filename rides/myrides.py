from typing import Annotated, Mapping, Any
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from pymongo.asynchronous.collection import AsyncCollection, ReturnDocument

from users.exceptions import UnauthorizedOperation
from .exceptions import RideNotFound
from .models import RideReq, RideDB
from dependencies import get_current_user
from users.models import UserDatabase
from db import db
from uuid import uuid4



@router.get("/my_rides")
async def my_rides_get_handler(current_user:Annotated[UserDatabase,Depends(get_current_user)],lim:int = 10):
    cursor = rides_collection.find({"created_by":current_user.id})
    rides = [ride async for ride in cursor]
    return JSONResponse(
        content={
            "rides":rides
        },
        status_code=status.HTTP_200_OK
    )