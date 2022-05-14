from routers.content.model import ContentDisplayForUser
from core.database.mongodb import get_collection_client
from ..config import COURSE_COLLECTION_NAME,CONTENT_COLLECTION_NAME
from typing import List
async def get_content(course_id:str):
    #initialize 
    content_all = []
    #get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    content_cursor = content_collection.find({"course_id":course_id})
    async for content in content_cursor:
        content_model = ContentDisplayForUser(**content)
        content_all.append(content_model.dict())
    return content_all