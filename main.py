import os
from typing import Mapping, Any, Annotated

from fastapi import FastAPI, Request, Depends
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.asynchronous.collection import AsyncCollection

from db import db
from dependencies import get_current_user
from rides import rides
from rides.exceptions import RideNotFound
from users import login,users
from users.exceptions import InvalidToken, UnauthorizedOperation, UserNotFound
from users.models import UserDatabase
from Chat import chat
from dev_tools import impersonate
rides_collection: AsyncCollection[Mapping[str, Any]] = db["rides"]


app = FastAPI()

# Include other routes here
# using app.include_router()
origins = [
    "http://localhost:3000",
    "http://localhost:4200",
    "https://capable-kleicha-4c058f.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidToken)
async def InvalidToken_exception_handler(request: Request, exc: InvalidToken):
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.detail,
            "received id": exc.id_token
        },
    )


@app.exception_handler(RideNotFound)
async def RideNotFound_exception_handler(request: Request, exc: RideNotFound):
    return JSONResponse(
        content={
            "ride":None,
            "detail": exc.detail,
            "requested ride id": exc.id,
        },
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(UnauthorizedOperation)
async def UnauthorizedOperation_exception_handler(request: Request, exc: UnauthorizedOperation):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": exc.detail,
            "resource id": exc.resource_id
        }
    )

@app.exception_handler(UserNotFound)
async def UserNotFound_exception_handler(request:Request,exc:UserNotFound):
    return JSONResponse(
        content={
            "detail":exc.detail,
            "Requested Id":exc.user_id,
        },
        status_code=404
    )

app.include_router(login.router)
app.include_router(rides.router)
app.include_router(users.router)
app.include_router(chat.router)

app.include_router(impersonate.router)
@app.get("/")
async def base_handler():
    return "Eventually you can hope to get some documentation from this endpoint"

@app.get("/my_rides")
async def my_rides_get_handler(current_user:Annotated[UserDatabase,Depends(get_current_user)],lim:int = 10):
    cursor = rides_collection.find({"created_by":current_user.id}).limit(lim)
    user_rides = [ride async for ride in cursor]
    return JSONResponse(
        content={
            "rides":user_rides
        },
        status_code=status.HTTP_200_OK
    )