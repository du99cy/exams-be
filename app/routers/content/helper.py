from routers.content.model import ContentDisplayForUser
from core.database.mongodb import get_collection_client
from ..config import COURSE_COLLECTION_NAME,CONTENT_COLLECTION_NAME
from typing import List
from bson.objectid import ObjectId

async def get_content(course_id:str):
    #initialize 
    content_all = []
    #get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    #get order content in course
    course_infor = await course_collection.find_one({"id":course_id,"status":2},{"order_contents":1})
    
    for content_id in course_infor["order_contents"]:
        content =await content_collection.find_one({"_id":ObjectId(content_id),"is_deleted":False})
        if content:
            content_model = ContentDisplayForUser(**content,id=str(content["_id"]))
            content_all.append(content_model.dict())
    return content_all

