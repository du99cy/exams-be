from fastapi import APIRouter, Body,HTTPException

from core.constants import TEMPLATE_EMAIL,FORGOT_PASSWORD_EMAIL_TEMP
from .dependencies import *
from .models import ConfirmToken, UserSignUp
from core.database.mongodb import get_collection_client
from typing import Any
from core.helpers_func import responseModel
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from .helper import SendEmail
from fastapi.encoders import jsonable_encoder
import json

api_router = APIRouter(tags=['Auth'], prefix="/auth")


@api_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": json.dumps(user.dict()) , "scopes": ["later"]},
        expires_delta=access_token_expires,
    )
    return jsonable_encoder({"user_infor":user,"access_token": access_token, "token_type": "bearer",'expire_token_time_minutes':ACCESS_TOKEN_EXPIRE_MINUTES})

@api_router.get("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": json.dumps(current_user.dict()) , "scopes": ["later"]},
        expires_delta=access_token_expires,
    )
    return jsonable_encoder({"access_token": access_token, "token_type": "bearer",'expire_token_time_minutes':ACCESS_TOKEN_EXPIRE_MINUTES})

@api_router.get("/users/me/")
async def read_users_me(current_user: User = Depends(get_current_active_user)):

    return responseModel(data=current_user.dict())  

@api_router.post("/sign-up")
async def sign_up(user_data: UserSignUp = Body(...)) -> Any:
    user_collection = await get_collection_client("user")
    confirm_token_collection = await get_collection_client('confirm_token')
    # initialize user id
    user_id = 0
    # check email is exists
    user_email_exists = await user_collection.find_one({"email": user_data.email})
    user_id = user_email_exists["_id"] if user_email_exists else user_id
    # save user data to user collection if not exists or user exists and not enabled(not activate)
    if not user_email_exists or not user_email_exists['enabled']:
        hashed_password = get_password_hash(user_data.password)
        user_insert_data_db_model = UserInDB(
            **user_data.dict(), hashed_password=hashed_password)
        user_insert_data_dict = user_insert_data_db_model.dict()
        del user_insert_data_dict['id']
        inserted_result = await user_collection.insert_one(user_insert_data_dict)
        user_id = inserted_result.inserted_id
    # if email exist and enabled or locked
    else:
        #if user_email_exists["enabled"]:
        return responseModel(message="email is existed", status_code=400)

    # create a token
    token = ObjectId()
    # save confirm token data
    created_at = datetime.now()
    # token expire is 15 minites
    expires_at = created_at + timedelta(minutes=15)
    confirn_token_model = ConfirmToken(token=str(
        token), created_at=created_at, expires_at=expires_at, user_id=str(user_id))
    # save confirm token data
    confirm_token_dict = confirn_token_model.dict()
    del confirm_token_dict['id']
    await confirm_token_collection.insert_one(confirm_token_dict)

    #send email
    temp = TEMPLATE_EMAIL.format(user_name=user_data.first_name + " " + user_data.last_name,activate_link=f"http://localhost:4200/confirm-token/{str(token)}")
    send_email_ins = SendEmail(temp,user_data.email)
    
    email_sent_result = await send_email_ins.send()
    return email_sent_result


@api_router.get("/confirm-token/{token}")
async def confirm_token(token: str) -> Any:
    # get collection
    user_collection = await get_collection_client("user")
    confirm_token_collection = await get_collection_client('confirm_token')

    # find token
    confirm_token_data = await confirm_token_collection.find_one({"token": token})
    if not confirm_token_data:
        raise HTTPException(status_code=400,detail="invalid token")
    if confirm_token_data['confirm_at']:
        raise HTTPException(status_code=400,detail="account have been activated")
    # get time now
    now = datetime.now()
    # save confirm token at time
    await confirm_token_collection.update_one({"_id": confirm_token_data["_id"]}, {"$set": {"confirm_at": now}})
    # check confirm token expire time
    if confirm_token_data['expires_at'] < now:
        
        return responseModel(status_code=400, message="confirm token expired",data={"notif":"Mã xác thực đã quá hạn .Hãy lấy lại mã xác thực"})
    else:
        # enable user
        await user_collection.update_one({"_id": ObjectId(confirm_token_data["user_id"])},{"$set":{"enabled":True}})
        return responseModel(status_code=200, message="get token success",data={"notif":"Kích hoạt tài khoản thành công ."})
    
@api_router.get('/forgot-password/{email_text}')
async def forgot_password(email_text:str):
   
    #get user collection
    user_collection = await get_collection_client("user")
    
     #check exist email
    user_data = await user_collection.find_one({"email":email_text,"enabled":True})
    if not user_data:
        raise HTTPException(status_code=404,detail="Email không tồn tại")
    
    #create strong password
    import secrets,string
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))

    #save new password to user
    hash_new_password = get_password_hash(password)
    user_collection.update_one({"email":email_text,"enabled":True},{"$set":{"hashed_password":hash_new_password}})
    
    #send password to email
    temp = FORGOT_PASSWORD_EMAIL_TEMP.format(new_password = password)
    send_email_ins = SendEmail(temp,email_text)
    
    email_sent_result = await send_email_ins.send()
    return email_sent_result