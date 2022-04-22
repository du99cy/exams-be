from..function.model import Parameter
from pydantic import BaseModel
from typing import List

class OutputTestCase(BaseModel):
    datatype: str | None =None
    value: str | None = None
    
class Testcase(BaseModel):
    id:str | None = None
    inputs:List[Parameter] | None = []
    output:OutputTestCase | None = None
    content_id:str | None = None
    course_id:str | None = None
    instructor_id: str | None = None
    is_deleted: bool | None = False
    created_at_seconds:int | None = None
    lock:bool | None = None
    