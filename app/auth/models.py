from typing import Optional,List

from pydantic import BaseModel,Field,EmailStr
from datetime import datetime


class User(BaseModel):
    id:Optional[str] = None
    first_name:  Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = Field(None,regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    enabled: Optional[bool] = False
    locked: Optional[bool] = False
    role_id:Optional[str] = None
    
class TokenData(BaseModel):
    user: Optional[User] = None
    scopes: List[str] = []

class UserInDB(User):
    hashed_password: str
    
class UserSignUp(User): 
    password: Optional[str] #= Field(None,regex=r'[A-Za-z0-9@#$%^&+=]{8,}')
    
class ConfirmToken(BaseModel): 
    id:Optional[str] = None
    token:Optional[str] = None
    confirm_at:Optional[datetime] = None
    created_at:Optional[datetime] = None
    expires_at:Optional[datetime] = None
    user_id:Optional[str] = None
    
class Token(BaseModel):
    user_infor:User 
    access_token: str
    token_type: str
    expire_token_time_minutes:int
    

    