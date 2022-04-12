from unittest.mock import Base
from pydantic import BaseModel


class Content(BaseModel):
    id: str | None = None
    title: str | None = None
    description: str | None = None
    type_status: int | None = None
    #type_status 0:lecture 1:quiz 2:coding
    course_id:str | None = None
    instructor_id: str | None = None
    create_date_seconds : int | None = None
    is_deleted:bool | None = False
    
