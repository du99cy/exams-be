from fastapi import APIRouter,Body,Path,Depends
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from core.helpers_func import responseModel
from .model import Testcase
import time
from ..config import COURSE_COLLECTION_NAME,TESTCASE_COLLECTION_NAME,CREDENTIALS_EXCEPTION
api_router = APIRouter(tags=['testcase'],prefix='/testcase')

@api_router.post("")
async def add_test_case(testcase:Testcase = Body(...),current_user = Depends(get_current_active_user)):
    #get collection
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    testcase_collection = await get_collection_client(TESTCASE_COLLECTION_NAME)
    
    #check auth
    is_allow = await course_collection.find_one({"id":testcase.course_id,"instructor_id": current_user.id})
    if not is_allow:
        raise CREDENTIALS_EXCEPTION
    
    testcase.instructor_id = current_user.id
    testcase.created_at_seconds = int(time.time())
    testcase_dict = testcase.dict()
    del testcase_dict['id']
    
    await testcase_collection.insert_one(testcase_dict)
    return responseModel()

@api_router.get("/{content_id}/all")
async def get_testcase_all(content_id:str= Path(...),current_user = Depends(get_current_active_user)):
    #get collection
 
    testcase_collection = await get_collection_client(TESTCASE_COLLECTION_NAME)
    
    #initialize
    testcase_list = []
    
    testcase_list_cursor = testcase_collection.find({"content_id":content_id, "instructor_id": current_user.id})
    async for testcase in testcase_list_cursor:
        testcase_model = Testcase(**testcase,id=str(testcase["_id"]))
        testcase_list.append(testcase_model.dict())
    
    return responseModel(data=testcase_list)