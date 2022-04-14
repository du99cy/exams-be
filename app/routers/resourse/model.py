from pydantic import BaseModel

class Resource(BaseModel):
    id:str | None = None
    name:str | None = None
    file:str | None = None
    type_code:int | None = None
    #0:video 1:file
    content_id:str | None = None
    course_id:str | None = None
    instructor_id:str | None = None
    size:int | None = None
    is_deleted:bool | None = False
    created_date_seconds:int | None = None