from pydantic import BaseModel, root_validator, Field


class UserReq(BaseModel):
    email:str
    name:str
    picture:str

class ReceivedToken(BaseModel):
    id_token:str

#This class wil help eventually parsing more information from the request
class UserDatabase(UserReq):
    id: str = Field(...,alias = "_id")  # Will be autofilled from email
#While data is being filled using UserDatabase() the constructor expects an _id argument
#it is to be accessed by object.id DONT USE ALIAS HERE
# While serializing it serializes without the id by default to do by alias set by_alias = true
# However pydantic's jsonable encoder takes the alias
# The convention followed in this code is to use _id only when sending and recieveing data from the database
# And use .id everywhere else

class AppToken(BaseModel):
    access_token:str
    token_type:str

class AppTokenData(BaseModel):
    id:str = Field(...,alias = "_id")

class UserRes(BaseModel):
    id:str = Field(...,alias = "_id")
    name:str