from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from .models import MailUser,UserInDB,TokenData,Token
from core.constants import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from core.database.mongodb import get_collection_client
import json

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": "$2b$12$gSvqqUPvlXP2tfVFaWK1Be7DlH.PKZbv5H8KnzzVgXXbVxpva.pFm",
        "disabled": True,
    },
}



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)





def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str):
    #get user collection
    user_collection = await get_collection_client("user")
    #get user information
    user_data_dict = await user_collection.find_one({"email":email,"enabled":True})
    if user_data_dict:
        return UserInDB(**user_data_dict,id=str(user_data_dict["_id"]))


async def authenticate_user(email: str, password: str):
    user:UserInDB = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return MailUser(**user.dict())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_json  = payload.get("sub")
        user = json.loads(user_json)
        if user is None:
            raise credentials_exception
        
        token_scopes = payload.get("scopes", [])
        user_model = MailUser(**user)
        
        token_data = TokenData(scopes=token_scopes, user=user_model)
        
    except (JWTError, ValidationError):
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user_model


async def get_current_active_user(
    current_user: MailUser = Security(get_current_user, scopes=[])
) -> MailUser:
    if current_user.locked:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



