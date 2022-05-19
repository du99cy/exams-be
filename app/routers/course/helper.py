from calendar import c
from ..config import COURSE_COLLECTION_NAME
from auth.dependencies import get_collection_client 
from .model import Course
from ..config import CREDENTIALS_EXCEPTION
from typing import List

async def get_course_infor(query:dict,projection:dict):
     # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    
    goals_result_dict = await course_collection.find_one(query,projection)
    if not goals_result_dict:
         raise CREDENTIALS_EXCEPTION
    goals_result_model = Course(**goals_result_dict,id=str(goals_result_dict["_id"]))
    
    return goals_result_model.dict(exclude_unset=True)

async def get_all_course(query ={},projection=None)->List[Course]:
    #initialize
    course_list = []
      # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

    courses_cursor = course_collection.find(query, projection)

    async for course in courses_cursor:
      
      course_model = Course(**course)
      course_list.append(course_model)
    return course_list 
      
async def get_courses_and_member_of_user(user_id:str):
  #initialize
  course_count = 0
  member_count = 0
  #get collections
  course_collection = await get_collection_client(COURSE_COLLECTION_NAME)

  course_list_cursor = course_collection.find({"instructor_id":user_id})
  async for course in course_list_cursor:
    course_count +=1
    member_count =+ len(course.get("learners_id",[]))
  
  return {"course_count":course_count, "member_count":member_count}

