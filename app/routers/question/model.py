
from pydantic import BaseModel
from typing import List
class Answer(BaseModel):
    id:str | None = None
    name:str | None = None
    description:str | None = None
    

class Question(BaseModel):
    id:str | None = None
    name:str | None = None
    description:str | None = None
    answers:List[Answer] | None=[]
    answers_right_id:List[str] | None = None
    question_type:str | None = None
    content_id:str | None =None
    instructor_id:str | None = None
    course_id:str | None = None
    created_at_seconds:int | None = None
    is_deleted:bool | None = False