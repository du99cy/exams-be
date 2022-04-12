from fastapi import APIRouter,Body, HTTPException,Depends
from .model import Content
from core.helpers_func import responseModel
import time
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from ..config import CONTENT_COLLECTION_NAME,COURSE_COLLECTION_NAME,CREDENTIALS_EXCEPTION
apiRouter = APIRouter(tags=['Content'],prefix='/content')

@apiRouter.post("")
async def add_lecture(current_user =Depends(get_current_active_user) ,content:Content = Body(...)):
    #get collections 
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    
    #check auth of user 
    user_is_instructor_of_this_course = await course_collection.find_one({"id":content.course_id,"instructor_id":current_user.id})
    
    if not user_is_instructor_of_this_course:
        raise CREDENTIALS_EXCEPTION
    
    content.create_date_seconds = int(time.time())
    content.instructor_id = current_user.id
    content_dict  = content.dict()
    del content_dict['id']
    try:
        insert_result = await content_collection.insert_one(content_dict)
        #update order content on course collection
        #push content id to order contents in course collection
        
        await course_collection.update_one({"id":content.course_id,"instructor_id":current_user.id},{"$push":{"order_contents":str(insert_result.inserted_id)}})
        
        return responseModel(status_code=200)
    except Exception as exp:
        raise HTTPException(status_code=400, detail="mongodb error")


    