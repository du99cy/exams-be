from .models.testcase_check import Testcase_Check
from ..config import FUNCTION_COLLECTION_NAME, TESTCASE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, CONTENT_COLLECTION_NAME
import time
from bson.objectid import ObjectId
from ..content.model import Content
from ..testcase.model import Testcase
from ..function.model import Function
from .models.code_template import CodeTemplate
from fastapi import APIRouter, Path, Query, Depends, Body
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from core.helpers_func import responseModel
from.models.language_type import LanguageType
from .models.python import Python
api_router = APIRouter(tags=['coding'], prefix='/coding')


@api_router.get("/content/{content_id}/function_template")
async def get_fucntion_template(content_id: str = Path(...), language: LanguageType = Query(...), current_user=Depends(get_current_active_user)):
    # get collections
    function_collection = await get_collection_client(FUNCTION_COLLECTION_NAME)
    testcase_collection = await get_collection_client(TESTCASE_COLLECTION_NAME)
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    # query condition
    conditions = {"content_id": content_id,
                  "instructor_id": current_user.id, "is_deleted": False}
    # get function information
    function_dict = await function_collection.find_one(conditions)
    function_model = Function(**function_dict, id=str(function_dict["_id"]))
    # gen template via function
    template = CodeTemplate(
        language_pro_name=language.value, func=function_model)
    # get testcase list
    testcase_list = []
    testcase_cursor = testcase_collection.find(conditions)
    async for testcase in testcase_cursor:
        
        testcase_model = Testcase_Check(**testcase, id=str(testcase["_id"]),expected_output=testcase["output"]["value"])
        testcase_list.append(testcase_model)
    # get contents
    content_dict = await content_collection.find_one({"_id": ObjectId(content_id), "instructor_id": current_user.id, "is_deleted": False})
    content_model = Content(**content_dict, id=content_id)
    data = {"content": content_model,
            'function': function_model,
            'testcase_list': testcase_list, 'template': str(template)}
    return responseModel(data=data)


@api_router.post("/content/{content_id}/run-testcase")
async def run_testcase(content_id: str = Path(...), current_user=Depends(get_current_active_user), language_program_name: str = Query(...), script: str = Body(...)):
    # get colections
    testcase_collection = await get_collection_client(TESTCASE_COLLECTION_NAME)
    function_collection = await get_collection_client(FUNCTION_COLLECTION_NAME)

    #get function infor
    function_dict = await function_collection.find_one({"content_id":content_id,"instructor_id": current_user.id, "is_deleted": False})
    function_model = Function(**function_dict, id=str(function_dict["_id"]))
    
    #get list testcase
    testcases = []
    testcase_cursor = testcase_collection.find({"content_id":content_id,"instructor_id": current_user.id, "is_deleted": False})
    async for testcase in testcase_cursor:
        testcase_model = Testcase(**testcase,id=str(testcase["_id"]))
        testcases.append(testcase_model)
        
    python  = Python(function_model,script,testcases)
    
    testcases_result = await python.run_testcase()
    
    return responseModel(data = testcases_result)
        
    
    
