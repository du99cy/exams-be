from ..config import COURSE_COLLECTION_NAME
from auth.dependencies import get_collection_client 
from .model import Course
from ..config import CREDENTIALS_EXCEPTION

async def get_course_infor(query:dict,projection:dict):
     # get collections
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    
    goals_result_dict = await course_collection.find_one(query,projection)
    if not goals_result_dict:
         raise CREDENTIALS_EXCEPTION
    goals_result_model = Course(**goals_result_dict,id=str(goals_result_dict["_id"]))
    
    return goals_result_model.dict(exclude_unset=True)
    