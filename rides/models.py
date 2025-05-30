from pydantic import BaseModel
from pydantic import Field
from datetime import datetime
from bson import ObjectId

from users.models import UserDatabase


# class RideDB(BaseModel):
#     id:str|None = Field(...,alias = "_id")
#     date:datetime
#     start:str
#     destination:str
#     total:int
#     user_ids:list[str]
#     created_by:str
#     last_updated:datetime

class RideReq(BaseModel):
    date:datetime
    start:str
    destination:str
    total:int

class RideDB(RideReq):
    id: str  = Field(alias="_id")
    users:list[str]
    created_by: str
    last_updated: datetime
