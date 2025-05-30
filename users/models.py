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

class AppToken(BaseModel):
    access_token:str
    token_type:str

class AppTokenData(BaseModel):
    id:str = Field(...,alias = "_id")