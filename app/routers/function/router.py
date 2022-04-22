from fastapi import APIRouter, Depends, Body, Path,Query
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from .model import Function
from ..config import COURSE_COLLECTION_NAME, FUNCTION_COLLECTION_NAME, CREDENTIALS_EXCEPTION
import time
from core.helpers_func import responseModel
api_router = APIRouter(tags=['Function'], prefix='/function')


@api_router.post("")
async def addFunction(function_body: Function = Body(...), current_user=Depends(get_current_active_user)):
    # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    function_collection = await get_collection_client(FUNCTION_COLLECTION_NAME)

    # check auth with course id
    is_allow = await course_collection.find_one({"id": function_body.course_id, "instructor_id": current_user.id})

    if not is_allow:
        raise CREDENTIALS_EXCEPTION
    function_body.instructor_id = current_user.id
    function_body.created_at_seconds = time.time()
    function_dict = function_body.dict()
    del function_dict['id']

    await function_collection.update_one({"content_id": function_body.content_id, "instructor_id": current_user.id}, {"$set": function_dict}, True)
    return responseModel

@api_router.get("/{content_id}")
async def get_func_via_content_id(content_id:str = Path(...),current_user = Depends(get_current_active_user)):
    #only user in class and instructor can get function
    #get collections
    function_collection = await get_collection_client(FUNCTION_COLLECTION_NAME)
    #check instructor(mode is preview)
    func_dict = await function_collection.find_one({"content_id":content_id,"instructor_id": current_user.id})
    #parse
    func_mode = Function(**func_dict,id=str(func_dict["_id"])) if func_dict else None
    
    return responseModel(data=func_mode)
    
    
    #check user in class (mode is learning)
    

    