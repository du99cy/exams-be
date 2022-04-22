from pydantic import BaseModel
from typing import List

class Parameter(BaseModel):
    id:str | None = None
    name:str | None = None
    datatype:str | None = None
    value:str | None = None
    
class Function(BaseModel):
    id:str | None = None
    name:str | None = None
    execution_time:int | None =None
    inputs:List[Parameter] | None = None
    output_data_type:str | None = None
    content_id: str | None = None
    course_id: str | None = None
    instructor_id: str | None = None
    is_deleted: bool | None = False
    created_at_seconds:int | None = None