

from fastapi import APIRouter,Path,Query,Depends
from auth.dependencies import get_current_active_user
from core.helpers_func import responseModel
from core.database.mongodb import get_collection_client
from ..config import MULTIPLE_CHOICES_COLLECTION_NAME
from .model import MultichoiceExamBase
from bson.objectid import ObjectId
multichoice_exam_router = APIRouter(tags=['MultichoiceExam'],prefix="/multichoice-exam")

@multichoice_exam_router.get("/{content_id}/history")
async def get_multichoice_exam_his(content_id:str = Path(...),current_user=Depends(get_current_active_user) ):
    #initialize
    exam_his_list = []
    #get collections
    multichoice_exam_collection = await get_collection_client(MULTIPLE_CHOICES_COLLECTION_NAME)

    exams_his = multichoice_exam_collection.find({"user_id":current_user.id,"content_id":content_id})

    async for exam_his in exams_his:
        exam_his_model = MultichoiceExamBase(**exam_his,id=str(exam_his["_id"]))
        exam_his_list.append(exam_his_model.dict())
    return responseModel(data=exam_his_list)

@multichoice_exam_router.get("/{multichoice_exam_id}")
async def get_multichoice_exam_his_details(multichoice_exam_id:str = Path(...), current_user=Depends(get_current_active_user)):
    
    # get collections

    multichoice_exam_collection = await get_collection_client(MULTIPLE_CHOICES_COLLECTION_NAME)

    multichoice_exam = await multichoice_exam_collection.find_one({"_id":ObjectId(multichoice_exam_id),"user_id":current_user.id})
    print(multichoice_exam)
    questions = multichoice_exam["questions"]
    return responseModel(data=questions)