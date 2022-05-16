from inspect import trace
from fastapi import APIRouter, Body, HTTPException, Depends, Path, Query, Request
from auth.helper_func import get_user_information
from auth.models import User
from routers.content.helper import get_content

from auth.models import MailUser
from .model import Course, CourseInforPublish
from core.database.mongodb import get_collection_client
from core.helpers_func import responseModel
import time
from auth.dependencies import get_current_active_user
from ..config import CONTENT_COLLECTION_NAME, COURSE_COLLECTION_NAME, USER_COLLECTION
from ..content.model import Content
from bson.objectid import ObjectId
from .helper import get_course_infor
from sse_starlette import EventSourceResponse
import json
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
        content = await content_collection.find_one({"_id": ObjectId(content_id),"is_deleted":False})
        # parse to content model
        if content:
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
                      "category": 1, "description": 1, "img": 1, "img_name": 1}
    elif mode == "price":
        projection = {"price": 1}
    elif mode == "goals":
        projection = {"who_course_is_for": 1,
                      "prerequisites": 1, "knowleages_will_learn": 1}
    else:
        projection = {}

    course_infor_data = await get_course_infor(query, projection)

    return responseModel(data=course_infor_data)


@course_router.get("/{course_id}/review")
async def course_review(course_id: str = Path(...), current_user=Depends(get_current_active_user)):
    # get collection
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # find course
    course_infor = await course_collection.find_one({"id": course_id, "instructor_id": current_user.id})
    del course_infor["_id"]
    # check all of null fields in course
    keys_of_null_value = [k for k, v in course_infor.items(
    ) if v is None or (isinstance(v, list) and len(v) == 0)]

    return responseModel(data=keys_of_null_value)


@course_router.get("/{course_id}/data-stream")
async def get_course_detail(request: Request, course_id: str = Path(...)):
    # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    # get course infor
    course = await course_collection.find_one({"id": course_id})
    course_model = CourseInforPublish(**course)

    async def event_generator():

        yield json.dumps({"data_name": "course", "data": course_model.dict()})
        # while True:
        #     # If client closes connection, stop sending events
        #     if await request.is_disconnected():
        #         break

        # Checks for new messages and return them to client if any

        user_model = await get_user_information(course_model.instructor_id)
        yield json.dumps({"data_name":"user","data": user_model.dict()})
        contents = await get_content(course_id=course_model.id)
        yield json.dumps({"data_name":"contents","data": contents})

    return EventSourceResponse(event_generator())
