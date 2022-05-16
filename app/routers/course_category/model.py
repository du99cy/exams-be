from pydantic import BaseModel

class CourseCategoryPost(BaseModel):
    name:str | None = None
    description:str | None = None

class CourseCategory(CourseCategoryPost):
    id:str | None = None
    