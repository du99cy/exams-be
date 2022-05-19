from ast import If
from unicodedata import category
from fastapi import APIRouter,Depends,Body,Path,HTTPException

from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from .model import CourseCategory,CourseCategoryPost
from ..config import COURSE_CATEGORY_NAME,CREDENTIALS_EXCEPTION
from core.helpers_func import responseModel
from bson.objectid import ObjectId
course_category_router = APIRouter(tags=["Course-Category"],prefix="/course-category")

@course_category_router.post("")
async def add_category(course_category_body:CourseCategoryPost = Body(...),current_user=Depends(get_current_active_user)):
    #get collections
    course_category_collection = await get_collection_client(COURSE_CATEGORY_NAME)
    print(current_user)
    #just admin can do this work
    if current_user.role_id != 1:
        raise CREDENTIALS_EXCEPTION
    
    course_category_dict = course_category_body.dict()
    if course_category_dict.get("id") is not None:
        del course_category_dict["id"]
    
    result_insert = await course_category_collection.insert_one(course_category_dict)

    return responseModel(data=str(result_insert.inserted_id))

@course_category_router.get("")
async def get_all_categories():
    #initialize
    cat_list = []
    #get collections
    course_category_collection = await get_collection_client(COURSE_CATEGORY_NAME)
    #just admin can do this work
    # if current_user.role_id != 1:
    #     raise CREDENTIALS_EXCEPTION
    
    course_category_cursor = course_category_collection.find({})
    async for cat in course_category_cursor:
        cat_model = CourseCategory(**cat, id=str(cat["_id"]))
        cat_list.append(cat_model.dict())
    return responseModel(data=cat_list)


@course_category_router.get("/{category_id}")
async def get_category_via_id(category_id:str = Path(...) ,current_user=Depends(get_current_active_user)):
    #get collections
    course_category_collection = await get_collection_client(COURSE_CATEGORY_NAME)
    #just admin can do this work
    if current_user.role_id != 1:
        raise CREDENTIALS_EXCEPTION
    
    category = await course_category_collection.find_one({"_id":ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404,detail="Not Found")
    category_model = CourseCategory(**category,id=str(category["_id"]))

    return responseModel(data=category_model.dict())

@course_category_router.delete("/{category_id}")
async def delete_category(category_id:str = Path(...) ,current_user=Depends(get_current_active_user)):
    #get collections
    course_category_collection = await get_collection_client(COURSE_CATEGORY_NAME)
    #just admin can do this work
    if current_user.role_id != 1:
        raise CREDENTIALS_EXCEPTION

    await course_category_collection.delete_one({"_id":ObjectId(category_id)})

    return responseModel()

@course_category_router.patch("/{category_id}")
async def update_category(category_id:str = Path(...),category_body:CourseCategoryPost= Body(...), current_user = Depends(get_current_active_user)):
    #get collections
    course_category_collection = await get_collection_client(COURSE_CATEGORY_NAME)
    #just admin can do this work
    if current_user.role_id != 1:
        raise CREDENTIALS_EXCEPTION

    category_dict = category_body.dict(exclude_unset=True)

    await course_category_collection.update_one({"_id":ObjectId(category_id)},{"$set":category_dict})

    return responseModel(data=category_id)