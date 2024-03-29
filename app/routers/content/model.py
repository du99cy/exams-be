from unittest.mock import Base
from pydantic import BaseModel
from typing import List

class ContentDisplayForUser(BaseModel):
    id: str | None = None
    title: str | None = None
    description: str | None = None
    type_status: int | None = None
    # type_status 0:lecture 1:quiz 2:coding
    course_id: str | None = None
     # if type is quiz then have more some properties
    time_for_quiz_minutes: int | None = 0
class Content(ContentDisplayForUser):
    instructor_id: str | None = None
    create_date_seconds: int | None = None
    is_deleted: bool | None = False
    questions_of_quiz_order: List[str] | None = []
    

