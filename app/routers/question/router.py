from calendar import c
from fastapi import APIRouter, Depends, Body, Path, Query,BackgroundTasks
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from .model import Question, QuestionListSaveDB, QuestionPostOfUser, QuestionWithRightAnswers
from ..config import CONTENT_COLLECTION_NAME, CREDENTIALS_EXCEPTION, MULTIPLE_CHOICES_COLLECTION_NAME, QUESTION_COLLECTION_NAME, COURSE_COLLECTION_NAME
from bson.objectid import ObjectId
from core.helpers_func import responseModel
from typing import List
api_router = APIRouter(tags=['Question'], prefix='/question')


@api_router.post('')
async def add_question(current_user=Depends(get_current_active_user), question_body: QuestionWithRightAnswers = Body(...)):
    # get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    contents_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    # check auth
    is_allow = await course_collection.find_one({"id": question_body.course_id, "instructor_id": current_user.id})
    if not is_allow:
        raise CREDENTIALS_EXCEPTION
    # assign instructor
    question_body.instructor_id = current_user.id
    question_dict = question_body.dict()
    # Note: include question id and answer id that user pass

    # insert to database
    await question_collection.insert_one(question_dict)
    # push to quiz order the do later
    # await content_collection.update_one({"_id":ObjectId(question_body.content_id)},{"$push":{"questions_of_quiz_order":question_body}})

    return responseModel()


@api_router.get("/{content_id}")
async def get_all_question_via_content_id(content_id: str = Path(...), current_user=Depends(get_current_active_user), mode: str = Query("learning")):
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)

    # initialize list returned
    question_list = []
    # if mode is preview
    question_cursor = question_collection.find(
        {"content_id": content_id, "is_deleted": False})
    async for question in question_cursor:
        #get right answer if user is instructor else not
        question_model = QuestionWithRightAnswers(**question) if question["instructor_id"] == current_user.id else Question(**question) 
        question_list.append(question_model)

    return responseModel(data=question_list)


@api_router.patch("/{question_id}")
async def update_question(question_id: str = Path(...), question_body_update: QuestionWithRightAnswers = Body(...), current_user=Depends(get_current_active_user)):
    # get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)

    question_body_update_dict = question_body_update.dict(exclude_unset=True)

    # update to database
    await question_collection.update_one({"id": question_id, "instructor_id": current_user.id, "is_deleted": False}, {"$set": question_body_update_dict}, False)
    return responseModel()


@api_router.delete("/{question_id}")
async def remove_question(question_id: str = Path(...), current_user=Depends(get_current_active_user)):
    # get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)

    # remove
    await question_collection.update_one({"id": question_id, "instructor_id": current_user.id}, {"$set": {"is_deleted": True}}, False)

    return responseModel()


@api_router.post("/multi-choice-exam/{content_id}")
async def post_multile_choice_exam(background_tasks: BackgroundTasks,content_id: str = Path(...), exam: List[QuestionPostOfUser] = Body(...), current_user=Depends(get_current_active_user)):
    # initialize
    right_question_count = 0
    question_total = 0
    question_list_his = []
    course_id = None
    question_list_with_right_answer = []
    # get collections
    question_collection = await get_collection_client(QUESTION_COLLECTION_NAME)
    multi_choice_exam_collection = await get_collection_client(MULTIPLE_CHOICES_COLLECTION_NAME)
    # check answer right and give mark numbers
    for question in exam:
        question_total += 1
        question_db = await question_collection.find_one({"id": question.id})
        question_db_model = QuestionWithRightAnswers(**question_db)
        #right answers to list
        question_list_with_right_answer.append({"id":question_db_model.id, "answers_right_id":question_db_model.answers_right_id})
        if course_id is None:
            course_id = question_db_model.course_id
        # check if right or wrong question
        
        if set(question.answers_of_student) == set(question_db_model.answers_right_id):
            
            right_question_count  = right_question_count +1

        question_his = QuestionWithRightAnswers(**{**question_db_model.dict(exclude_unset=True),**question.dict()})
        question_list_his.append(question_his)
    
    # save result to do
    examHistory = QuestionListSaveDB(
        user_id=current_user.id, score=f'{right_question_count}/{question_total}', content_id=content_id, course_id=course_id, questions=question_list_his)
    
    async def save_multiple_choice_exam(multi_choice_exam:QuestionListSaveDB):
        await multi_choice_exam_collection.insert_one(multi_choice_exam.dict())
    
    background_tasks.add_task(save_multiple_choice_exam,examHistory)
    data_returned = {"score":f'{right_question_count}/{question_total}',"right_answer_id_of_question_data_list":question_list_with_right_answer,"mode":"view"}
    return responseModel(data=data_returned)

