from calendar import c
from inspect import trace
from fastapi import APIRouter, Body, HTTPException, Depends, Path, Query, Request
from auth.helper_func import get_user_information
from auth.models import User
from routers.content.helper import get_content

from auth.models import MailUser
from .model import Course, CourseInforPublish, CourseSummaryInHomePage
from core.database.mongodb import get_collection_client
from core.helpers_func import responseModel
import time
from auth.dependencies import get_current_active_user
from ..config import CONTENT_COLLECTION_NAME, COURSE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, USER_COLLECTION
from ..content.model import Content
from bson.objectid import ObjectId
from .helper import get_course_infor, get_courses_and_member_of_user
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

#get for admin
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
async def get_all_content(current_user=Depends(get_current_active_user), course_id: str = Path(...),mode:str = Query("learning")):
    query={"id": course_id}
    projection = {"_id": 0, "order_contents": 1}
    
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    content_list = []
    # initialize result list
    is_admin = await course_collection.find_one({"id":course_id,"instructor_id": current_user.id},projection)
    if is_admin:
        ...
    
    else:
        user_is_bought = await course_collection.find_one({"id":course_id,"learners_id":{"$in":[current_user.id]}})
        if not user_is_bought:
            raise CREDENTIALS_EXCEPTION
    
        
    # get content id via order content in course collection
    course_details = await course_collection.find_one(query,projection)
    
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
    keys_of_null_value=[] if  keys_of_null_value[0] =='learners_id' else keys_of_null_value
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
#get for user
@course_router.get("/all/published")
async def get_published_courses():
    #initialize
    data_returned = {}
    #get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    courses_cursor = course_collection.find({"is_published": True})

    async for course in courses_cursor:
        course_model = CourseSummaryInHomePage(**course)

        data_returned.setdefault(course_model.category,[])
        data_returned[course_model.category].append(course_model.dict())
    
    return responseModel(data=data_returned)
@course_router.get("/{course_id}/published")
async def get_courses_published(course_id:str = Path(...)):
     #get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    course = await course_collection.find_one({"is_published": True,"id": course_id})
    if course:
        course_model = CourseSummaryInHomePage(**course)
        return responseModel(data=course_model.dict())
    raise HTTPException(status_code=404,detail="not found")

@course_router.get("/courses/me")
async def get_my_purchase_courses(current_user=Depends(get_current_active_user)):
    #initialize
    course_list = []
    # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    courses = course_collection.find({"learners_id":{"$in":[current_user.id]}})

    async for course in courses:
        course_model = CourseSummaryInHomePage(**course)
        course_list.append(course_model.dict())
    return responseModel(data=course_list)

@course_router.get("/statistical-users")
async def get_all_user_infor_about_courses_and_members(current_user=Depends(get_current_active_user)):
    #check auth

    if current_user.role_id !=1:
        raise CREDENTIALS_EXCEPTION
    #initialize
    user_data_returned =[]
    #get collections
    user_collection = await get_collection_client(USER_COLLECTION)
    users = user_collection.find({},{"first_name":1,"last_name":1})
    async for user in users:
        course_and_member_count =  await get_courses_and_member_of_user(str(user["_id"]))
        user = {**user,**course_and_member_count}
        user["id"]= str(user["_id"])
        del user["_id"]
        if course_and_member_count["course_count"] != 0:
            user_data_returned.append(user)
    return responseModel(data=user_data_returned)

