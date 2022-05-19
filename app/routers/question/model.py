
from pydantic import BaseModel
from typing import List
import time

class Answer(BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None

class QuestionPostOfUser(BaseModel):
    id:str | None = None
    answers_of_student: List[str] | None = []
class Question(QuestionPostOfUser):
    # id: str | None = None
    name: str | None = None
    description: str | None = None
    answers: List[Answer] | None = []
    # answers_of_student: List[str] | None = []
    question_type: str | None = None
    content_id: str | None = None
    instructor_id: str | None = None
    course_id: str | None = None
    created_at_seconds: int | None = None
    is_deleted: bool | None = False


class QuestionWithRightAnswers(Question):
    
    answers_right_id: List[str] | None = []

class QuestionListSaveDB(BaseModel):
    user_id:str | None = None
    score : str | None = None
    content_id: str | None = None
    course_id: str | None = None
    questions:List[QuestionWithRightAnswers] | None = []
    created_at_seconds_epoch_time: int | None = int(time.time())