from typing import Annotated, Mapping, Any
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from pymongo.asynchronous.collection import AsyncCollection
from users.exceptions import UnauthorizedOperation
from .exceptions import RideNotFound
from .models import RideReq, RideDB
from dependencies import get_current_user
from users.models import UserDatabase
from db import db
from uuid import uuid4
from users.users import get_username

rides_collection: AsyncCollection[Mapping[str, Any]] = db["rides"]

router = APIRouter(
    prefix="/rides",
    tags=["rides"],
)


# Creates a ride
@router.put("")
async def rides_put_handler(
        ride_req: RideReq,
        current_user: Annotated[UserDatabase, Depends(get_current_user)]
) -> JSONResponse:
    print(type(ride_req), ride_req, )
    ride_db: RideDB = RideDB(_id=str(uuid4()),
                             users=[current_user.id],
                             created_by=current_user.id,
                             last_updated=datetime.now().replace(second=0, microsecond=0),
                             **jsonable_encoder(ride_req))

    await rides_collection.insert_one(jsonable_encoder(ride_db, by_alias=True))
    return JSONResponse(
        content={"ride": {
            **jsonable_encoder(ride_db),
            "created_by": {"id": ride_db.created_by,
                           "name": await get_username(ride_db.created_by), },
            "users": [({"id": user, "name": await get_username(user)}) for user in ride_db.users],
            "is_in": (current_user.id in ride_db.users),
            "is_owner": (ride_db.created_by == current_user.id),
        }},
        status_code=status.HTTP_201_CREATED,
    )


@router.get("")
async def rides_get_handler(current_user: Annotated[UserDatabase, Depends(get_current_user)], lim: int = 10, ):
    cursor = rides_collection.find().sort("date", 1).limit(lim)
    rides = []
    async for ride in cursor:
        ride = {**ride}
        ride["id"] = ride["_id"]
        del ride["_id"]
        rides.append(
            {
                **ride,
                "created_by": {"id": ride.get("created_by"),
                               "name": await get_username(ride.get("created_by")), },
                "users": [({"id": user, "name": await get_username(user)}) for user in ride.get("users")],
                "is_in": (current_user.id in ride.get("users")),
                "is_owner": (ride.get("created_by") == current_user.id),
            }
        )
    return JSONResponse(
        content={
            "rides": rides,
            "status_code": status.HTTP_200_OK
        }
    )


@router.get("/{ride_id}")
async def rides_get_handler(ride_id: str, current_user: Annotated[UserDatabase, Depends(get_current_user)]):
    # ride_res = await rides_collection.find_one({"_id": ride_id})
    # ride_res = {
    #     **ride_res,
    #     "is_in": ride_res.get("user_ids").includes(current_user.id),
    #     "is_owner": (ride_res.get("created_by") == current_user.id),
    # }
    # # is_in and is_owner must be verified by backend again when accepting a change as these requests can
    # # be intercepted and changed
    # if ride_res:
    #     return JSONResponse(
    #         status_code=status.HTTP_200_OK,
    #         content={
    #             "ride": ride_res
    #         }
    #     )
    #
    # else:
    #     raise RideNotFound('Ride not found', ride_id)

    ride_res = await rides_collection.find_one({"_id":ride_id})

    if not ride_res:
        raise RideNotFound('Ride not found',ride_id)

    ride_res = {**ride_res}
    ride_res["id"] = ride_res["_id"]
    del ride_res["_id"]
    ride_res = {
                **ride_res,
                "created_by": {"id": ride_res.get("created_by"),
                               "name": await get_username(ride_res.get("created_by")), },
                "users": [({"id": user, "name": await get_username(user)}) for user in ride_res.get("users")],
                "is_in": (current_user.id in ride_res.get("users")),
                "is_owner": (ride_res.get("created_by") == current_user.id),
            }

    return JSONResponse(
        content={"ride":ride_res},
        status_code=200,
    )


#TODO Add a class that defines the structure of ride response and a function that can transform a ride_db into ride_response.


@router.patch("/{ride_id}")
async def rides_get_handler(ride_id: str, ride_req: RideReq,
                            current_user: Annotated[UserDatabase, Depends(get_current_user)]):
    ride_before = await rides_collection.find_one({"_id": ride_id})
    if not ride_before:
        raise RideNotFound("No ride found to update", ride_id)
    if not ride_before.get("created_by") == current_user.id:
        raise UnauthorizedOperation("Update not authorized", ride_id)

    update_data = {
        **ride_req.model_dump(),
        "last_updated": datetime.now().replace(second=0, microsecond=0)
    }

    await rides_collection.update_one(ride_before, {"$set": jsonable_encoder(update_data)})
    return JSONResponse(
        content=jsonable_encoder(update_data),
        status_code=status.HTTP_200_OK,
    )


@router.patch("/{ride_id}/join")
async def ride_join_handler(ride_id: str, current_user: Annotated[UserDatabase, Depends(get_current_user)]):
    ride = RideDB(**(await rides_collection.find_one({"_id": ride_id})))

    # Server side check to see if user is already a part of the ride
    if current_user.id in ride.users:
        return JSONResponse(
            content={"status": "User already in ride"},
            status_code=200,
        )

    # Should never go below zero but in case something goes critically wrong
    if (ride.total - len(ride.users)) <= 0:
        return JSONResponse(
            content={"status": "No place left in the ride"},
            status_code=200,
        )

    # Update operations
    ride.users.append(current_user.id)
    ride.last_updated = datetime.now().replace(second=0, microsecond=0)

    await rides_collection.find_one_and_update({"_id": ride_id}, {
        "$set": jsonable_encoder(ride, by_alias=True)
    }, return_document=False)

    # Ride is updated in place
    return JSONResponse(
        content={
            "ride": {**jsonable_encoder(ride, by_alias=False),
                     "created_by": {"id": ride.created_by,
                                    "name": await get_username(ride.created_by), },
                     "users": [({"id": user, "name": await get_username(user)}) for user in ride.users],
                     "is_in": (current_user.id in ride.users),
                     "is_owner": (ride.created_by == current_user.id), }
        },
        status_code=status.HTTP_200_OK,
    )
