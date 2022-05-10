from inspect import trace
from fastapi import APIRouter, Body, HTTPException, Depends, Path, Query

from auth.models import MailUser
from .model import Course
from core.database.mongodb import get_collection_client
from core.helpers_func import responseModel
import time
from auth.dependencies import get_current_active_user
from ..config import CONTENT_COLLECTION_NAME, COURSE_COLLECTION_NAME
from ..content.model import Content
from bson.objectid import ObjectId
from .helper import get_course_infor
course_router = APIRouter(tags=['Course'], prefix='/course')


@course_router.post("")
async def new_course_creation(current_user=Depends(get_current_active_user), course: Course = Body(...)):
    # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    # check document exists
    course_exists = await course_collection.find_one({"id": course.id})
    if course_exists:
        raise HTTPException(
            status_code=400, detail="have been exists course in system")
    course.instructor_id = current_user.id
    course.created_date_seconds = int(time.time())
    course_dict = course.dict()

    # add to mongodb
    result = await course_collection.insert_one(course_dict)
    return responseModel(status_code=200) if result else None


@course_router.get("/all")
async def get_all_course(current_user: MailUser = Depends(get_current_active_user)):
    course_list = []
    # get collection
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    courses_of_me = course_collection.find({"instructor_id": current_user.id})

    # convert to Course Model
    async for course in courses_of_me if courses_of_me else []:
        course_model = Course(**course)
        course_list.append(course_model)

    return responseModel(data=course_list)


@course_router.get("/{course_id}/content/all")
async def get_all_content(current_user=Depends(get_current_active_user), course_id: str = Path(...)):
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    # initialize result list
    content_list = []

    # get content id via order content in course collection
    course_details = await course_collection.find_one({"id": course_id, "instructor_id": current_user.id}, {"_id": 0, "order_contents": 1})
    order_contents = course_details['order_contents']

    # trace for order content list

    for content_id in order_contents:
        content = await content_collection.find_one({"_id": ObjectId(content_id)})
        # parse to content model
        content_model = Content(**content, id=content_id)
        content_list.append(content_model.dict())

    return responseModel(data=content_list)


@course_router.patch("/{course_id}")
async def update_course_detail(course_id: str = Path(...), current_user=Depends(get_current_active_user), course_body_update: Course = Body(...)):
    # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    course_body_update_dict = course_body_update.dict(exclude_unset=True)

    try:
        await course_collection.update_one({"id": course_id, 'instructor_id': current_user.id}, {"$set": course_body_update_dict}, False)
        return responseModel(status_code=200)
    except Exception as exp:
        raise HTTPException(status_code=400, detail=exp.message)


@course_router.get("/{course_id}/infor")
async def get_goals(current_user=Depends(get_current_active_user), course_id: str = Path(...), mode: str = Query("goals")):

    query = {"id": course_id, "instructor_id": current_user.id}
    projection = {"who_course_is_for": 1,
                  "prerequisites": 1, "knowleages_will_learn": 1}

    if mode == "course-landing-page":
        projection = {"title": 1, "teaching_language": 1,
                      "category": 1, "description": 1, "img": 1,"img_name":1}
    elif mode =="price":
        projection = {"price": 1}
    else:
        projection = {}

    course_infor_data = await get_course_infor(query, projection)

    return responseModel(data=course_infor_data)
