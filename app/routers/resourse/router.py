from http.client import HTTPException
import re
from fastapi import APIRouter, File, Query, UploadFile, Depends, Body, HTTPException, Path
from core.helpers_func import responseModel
import aiofiles
import os
from core.helpers_func import responseModel
from auth.dependencies import get_current_active_user
from .model import Resource
from core.database.mongodb import get_collection_client
from ..config import CONTENT_COLLECTION_NAME, COURSE_COLLECTION_NAME, RESOURSE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, RESOURSE_FILE_NAME, STATIC_FILE
import time
from fastapi.responses import FileResponse
from bson.objectid import ObjectId
api_router = APIRouter(tags=["Resourse"], prefix="/resourse")

# there is 2 mode :private file and public file :
# private file is file that can authen before get file
# public file is file that everyone can get it


@api_router.post("/uploadFile", dependencies=[Depends(get_current_active_user)])
async def uploadFile(file: UploadFile = File(...), mode: str = Query("private")):
    folder_name = STATIC_FILE if mode == 'public' else RESOURSE_FILE_NAME
    file_path = os.path.join(folder_name, file.filename)
    async with aiofiles.open(file_path, 'wb+') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return responseModel(data={'file': file_path})


@api_router.post("")
async def add_resourse(current_user=Depends(get_current_active_user), resourse: Resource = Body(...)):
    # get collections
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    # checkout auth :whether is exists user along with that course
    course = await course_collection.find_one({"id": resourse.course_id, "instructor_id": current_user.id})

    if not course:
        raise CREDENTIALS_EXCEPTION

    resourse.instructor_id = current_user.id
    resourse.created_date_seconds = int(time.time())
    resourse_dict = resourse.dict()
    del resourse_dict['id']
    try:
        insert_result = await resourse_collection.insert_one(resourse_dict)
        return responseModel(data=str(insert_result.inserted_id))
    except Exception as exp:
        raise HTTPException(status_code=400, detail=exp.message)


@api_router.get("/{content_id}/video", response_class=FileResponse)
async def get_video_of_content(content_id: str = Path(...), mode: str | None = Query(None), current_user=Depends(get_current_active_user)):
    # get collections
    content_collection = await get_collection_client(CONTENT_COLLECTION_NAME)
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)

    # initialize
    file_path = ''
    # mode is preview then check current user is instructor
    if mode == 'preview':
        video_resourse_doc = await resourse_collection.find_one({"content_id": content_id, "instructor_id": current_user.id, "type_code": 0, "is_deleted": False}, {"file": 1})
        file_path = video_resourse_doc['file']

    # mode is for student then check user have enrolled in that course

    return file_path
# get file response


@api_router.get("/{resourse_id}", response_class=FileResponse)
async def get_file_response(resourse_id: str = Path(...), current_user=Depends(get_current_active_user), mode: str = Query('preview')):
    # get collections
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)
    # initilize
    query = {"_id": ObjectId(resourse_id), "is_deleted": False}
    # if it is instructor
    if mode == 'preview':
        query.update({"instructor_id": current_user.id})
    else:
        # just a student
        pass
    resourse_data = await resourse_collection.find_one(query)
    return resourse_data["file"]


@api_router.delete("/{resourse_id}")
async def delete_resourse(resourse_id: str = Path(...), current_user=Depends(get_current_active_user)):
    # get collections
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)

    await resourse_collection.update_one({"_id": ObjectId(resourse_id), "instructor_id": current_user.id}, {"$set": {"is_deleted": True}})

    return responseModel()


@api_router.get("/{content_id}/all")
async def getAllResourses(content_id: str = Path(...), current_user=Depends(get_current_active_user), mode: str = Query("preview"), resourse_type: str = Query("all")):
    #get collections
    resourse_collection = await get_collection_client(RESOURSE_COLLECTION_NAME)

    #initialize value
    resourses = []

    query = {"content_id": content_id,"is_deleted": False}
    if mode == 'preview':
        query.update({"instructor_id": current_user.id})
    #if student then auth before return
    if resourse_type == "video":
        query.update({"type_code":0})
    if resourse_type == "file":
        query.update({"type_code":1})

    resourses_cursor = resourse_collection.find(query)
    async for resourse in resourses_cursor:
        resourses_model = Resource(**resourse,id=str(resourse["_id"]))    
        resourses.append(resourses_model.dict())
    return responseModel(data=resourses)