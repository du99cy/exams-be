from lib2to3.pytree import Base
from pydantic import BaseModel
from typing import List


class CourseSummaryInHomePage(BaseModel):
    id:str | None  = None
    title:str | None = None
    knowleages_will_learn:List[str] | None = []
    description:str | None = None
    price:float | None = None
    category:str | None = None
    img:str | None = None
    teaching_language:str | None = "tiếng việt"
class CourseInforPublish(CourseSummaryInHomePage):
    
    prerequisites :List[str] | None = []
    who_course_is_for:List[str] |None  = []
    instructor_id:str | None =  None
class Course(CourseInforPublish):   
    order_contents :List[str] | None = []
    is_published:bool | None = False
    img_name:str | None = None
    created_date_seconds:int | None = None
    status:int | None = 2
    learners_id:List[str] | None = []

'''
status:
    0:removed
    1:locked
    2:waiting_accept
    3:edit
    4:open
'''
    