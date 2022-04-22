from fastapi import APIRouter,Depends,Body,Path,Query
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from .model import Question, QuestionForStudent
from ..config import CONTENT_COLLECTION_NAME, CREDENTIALS_EXCEPTION,QUESTION_COLLECTION_NAME,COURSE_COLLECTION_NAME
from bson.objectid import ObjectId
from core.helpers_func import responseModel
api_router = APIRouter(tags = ['Question'],prefix='/question')

@api_router.post('')
async def add_question(current_user=Depends(get_current_active_user),question_body:Question = Body(...)):
    #get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    contents_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    #check auth
    is_allow = await course_collection.find_one({"id": question_body.course_id, "instructor_id": current_user.id})
    if not is_allow:
        raise CREDENTIALS_EXCEPTION
    #assign instructor
    question_body.instructor_id = current_user.id
    question_dict = question_body.dict()
    #Note: include question id and answer id that user pass
    
    #insert to database
    await question_collection.insert_one(question_dict)
    #push to quiz order the do later
    #await content_collection.update_one({"_id":ObjectId(question_body.content_id)},{"$push":{"questions_of_quiz_order":question_body}})
    
    return responseModel()

@api_router.get("/{content_id}")
async def get_all_question_via_content_id(content_id:str = Path(...),current_user = Depends(get_current_active_user),mode:str = Query("learning")):
    #get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    
    #initialize list returned
    question_list = []
    #if mode is preview
    question_cursor = question_collection.find({"content_id":content_id,"instructor_id":current_user.id,"is_deleted":False})
    async for question in question_cursor:
        question_model = QuestionForStudent(**question)
        question_list.append(question_model)
    
    return responseModel(data=question_list)

@api_router.patch("/{question_id}")
async def update_question(question_id:str=  Path(...),question_body_update:Question = Body(...),current_user = Depends(get_current_active_user)):
    #get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    
    question_body_update_dict = question_body_update.dict(exclude_unset=True)
    
    #update to database
    await question_collection.update_one({"id":question_id,"instructor_id": current_user.id,"is_deleted":False},{"$set":question_body_update_dict},False)
    return responseModel()
@api_router.delete("/{question_id}")
async def remove_question(question_id:str = Path(...),current_user = Depends(get_current_active_user)):
    #get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    
    #remove
    await question_collection.update_one({"id":question_id,"instructor_id": current_user.id},{"$set":{"is_deleted":True}},False)
    
    return responseModel()


    
    
    
    
    