from fastapi import APIRouter, Body, HTTPException, Depends, Path
from .model import Content
from core.helpers_func import responseModel
import time
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from ..config import CONTENT_COLLECTION_NAME, COURSE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, RESOURSE_COLLECTION_NAME
from bson.objectid import ObjectId
from ..resourse.model import Resource
apiRouter = APIRouter(tags=['Content'], prefix='/content')


@apiRouter.post("")
async def add_lecture(current_user=Depends(get_current_active_user), content: Content = Body(...)):
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # check auth of user
    user_is_instructor_of_this_course = await course_collection.find_one({"id": content.course_id, "instructor_id": current_user.id})

    if not user_is_instructor_of_this_course:
        raise CREDENTIALS_EXCEPTION

    content.create_date_seconds = int(time.time())
    content.instructor_id = current_user.id
    content_dict = content.dict()
    del content_dict['id']
    try:
        insert_result = await content_collection.insert_one(content_dict)
        # update order content on course collection
        # push content id to order contents in course collection

        await course_collection.update_one({"id": content.course_id, "instructor_id": current_user.id}, {"$push": {"order_contents": str(insert_result.inserted_id)}})

        return responseModel(status_code=200)
    except Exception as exp:
        raise HTTPException(status_code=400, detail="mongodb error")


@apiRouter.patch("/{content_id}")
async def updateAContent(content_id: str = Path(...), content_body_update: Content = Body(...), current_user=Depends(get_current_active_user)):
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)

    content_body_update = content_body_update.dict(exclude_unset=True)

    # update to database
    await content_collection.update_one({"_id": ObjectId(content_id), "instructor_id": current_user.id}, {"$set": content_body_update}, False)
    return responseModel()


@apiRouter.get("/{content_id}/resourses")
async def get_resourses_via_content_id(content_id: str = Path(...), current_user=Depends(get_current_active_user)):
    # get collections
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)

    video_resourse_list = []
    file_resourse_list = []

    resourse_cusor = resourse_collection.find(
        {"content_id": content_id, "instructor_id": current_user.id})
    async for resourse in resourse_cusor:
        resourse_model = Resource(**resourse, id=str(resourse["_id"]))
        if resourse_model.type_code == 0:
            video_resourse_list.append(resourse_model)
        else:
            file_resourse_list.append(resourse_model)
    return responseModel(data={"video_resourse_list": video_resourse_list, "file_resourse_list": file_resourse_list})
