import re
from fastapi import APIRouter, Body, Path, Depends
from auth.helper_func import get_user_information

from routers.course_rating.model import CourseRatingBase, CourseRatingDisplay, CourseRatingPost
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from ..config import COURSE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, RATING_COURSE_COLLECTION_NAME
from core.helpers_func import responseModel
from bson.objectid import ObjectId
CourseRatingRouter = APIRouter(tags=["Course-Rating"], prefix="/course-rating")


@CourseRatingRouter.post("/")
async def add_rating_course(ratingCourseBody: CourseRatingPost = Body(...), current_user=Depends(get_current_active_user)):
    # get collections
    rating_course_collection = await get_collection_client(RATING_COURSE_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # check auth
    # user must in course then rating that course
    is_allow = await course_collection.find_one({"id": ratingCourseBody.course_id, "learners_id": {"$in": [current_user.id]}})

    if not is_allow:
        raise CREDENTIALS_EXCEPTION
    else:
        course_rating_base_model = CourseRatingBase(
            **ratingCourseBody.dict(), learner_id=current_user.id)
       
        res_inserted = await rating_course_collection.insert_one(course_rating_base_model.dict())
        return responseModel(data=str(res_inserted.inserted_id))


@CourseRatingRouter.get("/course/{course_id}/rating-all")
async def get_all_rating_of_course(course_id: str = Path(...)):
    # initialize
    rating_list = []
    # get collections
    rating_course_collection = await get_collection_client(RATING_COURSE_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # user must in course then rating that course
    

    rating_cursor = rating_course_collection.find({"course_id": course_id})
    async for rating in rating_cursor:
        
        user_infor = await get_user_information(rating["learner_id"])

        rating_model = CourseRatingDisplay(
            **rating, id=str(rating["_id"]), learner_name=f"{user_infor.first_name} {user_infor.last_name}", learner_img=user_infor.avatar_pic)

        rating_list.append(rating_model.dict())
    return responseModel(data=rating_list)


@CourseRatingRouter.patch("/{rating_id}")
async def update_rating_course(rating_id: str = Path(...), ratingBodyUpdate: CourseRatingBase = Body(...), current_user=Depends(get_current_active_user)):
    # get collections
    rating_course_collection = await get_collection_client(RATING_COURSE_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # check auth
    # user must in course then rating that course
    is_allow = await course_collection.find_one({"_id": ObjectId(rating_id), "learner_id": current_user.id})

    if not is_allow:
        raise CREDENTIALS_EXCEPTION

    rating_body_update_dict = ratingBodyUpdate.dict(exclude_unset=True)
    await rating_course_collection.update_one({"_id": ObjectId(rating_id)}, {"$set": rating_body_update_dict})

    return responseModel(data=rating_id)


@CourseRatingRouter.delete("/{rating_id}")
async def delete_rating_course(rating_id: str = Path(...), current_user=Depends(get_current_active_user)):
    # get collections
    rating_course_collection = await get_collection_client(RATING_COURSE_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    # check auth
    # user must in course then rating that course
    is_allow = await course_collection.find_one({"_id": ObjectId(rating_id), "learner_id": current_user.id})

    if not is_allow:
        raise CREDENTIALS_EXCEPTION

    await rating_course_collection.delete_one({"_id": ObjectId(rating_id)})
    return responseModel(data=rating_id)


