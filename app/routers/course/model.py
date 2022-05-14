from pydantic import BaseModel
from typing import List

class CourseInforPublish(BaseModel):
    id:str | None  = None
    title:str | None = None
    knowleages_will_learn:List[str] | None = []
    prerequisites :List[str] | None = []
    description:str | None = None
    who_course_is_for:List[str] |None  = []
    price:float | None = None
    category:str | None = None
    img:str | None = None
    teaching_language:str | None = "tiếng việt"
    instructor_id:str | None =  None
class Course(CourseInforPublish):   
    order_contents :List[str] | None = []
    is_published:bool | None = False
    img_name:str | None = None
    created_date_seconds:int | None = None
    status:int | None = 2
    
'''
status:
    0:removed
    1:locked
    2:opened
'''
    