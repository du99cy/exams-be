from bson.objectid import ObjectId
from typing import List

from routers.config import USER_COLLECTION
from .models import FacebookUser, User,MailUser
from .dependencies import get_collection_client
async def get_user_information(user_id:str):
    #get collections
    user_collection = await get_collection_client(USER_COLLECTION)
    #function for get instructor information
    
    user = await user_collection.find_one({"_id":ObjectId(user_id)})
    if user : 
        if user.get("id") is not None:
            del user["id"]
    
        user_data = MailUser(**user,id=str(user["_id"])) if user["account_type"]=="mail" else FacebookUser(**user,id=str(user["_id"])) 
        return user_data
    return None

