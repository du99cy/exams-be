from pydantic import BaseModel

from routers import question
from typing import List
from ..question.model import QuestionWithRightAnswers
class MultichoiceExamBase(BaseModel):
    id : str | None = None
    score : str | None= None
    created_at_seconds_epoch_time:int | None= None

class MultichoiceExam(MultichoiceExamBase):
    questions:List[QuestionWithRightAnswers] | None = []