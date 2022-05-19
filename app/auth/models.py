from typing import Optional, List,Any

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from core.constants import ACCESS_TOKEN_EXPIRE_MINUTES

from core.constants import AVATAR_PIC_DEFAULT


class User(BaseModel):
    id: Optional[str] = None
    first_name:  Optional[str] = None
    last_name: Optional[str] = None
    locked: Optional[bool] = False
    avatar_pic: Optional[str] = Field(AVATAR_PIC_DEFAULT)
    headline: Optional[str] = None
    biography: Optional[str] = None
    amount_of_money: Optional[float] = 0
    facebook_link:Optional[str] = None
    youtube_link: Optional[str] = None
    website_link: Optional[str] = None
    twitter_link: Optional[str] = None
    role_id: Optional[Any] = None


class FacebookUser(User):
    facebook_id: Optional[str] = None
    account_type: Optional[str] = Field("facebook")

class MailUser(User):
    enabled: Optional[bool] = False
    email: Optional[str] = Field(
        None, regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    account_type: Optional[str] = Field("mail")


class TokenData(BaseModel):
    user: Optional[MailUser | FacebookUser] = None
    scopes: List[str] = []


class UserInDB(MailUser):
    hashed_password: str


class UserSignUp(MailUser):
    password: Optional[str]  # = Field(None,regex=r'[A-Za-z0-9@#$%^&+=]{8,}')


class ConfirmToken(BaseModel):
    id: Optional[str] = None
    token: Optional[str] = None
    confirm_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None


class Token(BaseModel):
    user_infor: Any = None
    access_token: str | None = None
    token_type: str = Field("bearer")
    expire_token_time_minutes: int  = Field(ACCESS_TOKEN_EXPIRE_MINUTES)

class ChangingPasswordModel(BaseModel):
    old_password:str
    new_password:str