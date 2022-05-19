from pydantic import BaseModel
import time
class CourseRatingPost(BaseModel):
    
    course_id: str | None = None
    comment: str | None = None
    star_number:int | None = None

class CourseRatingBase(CourseRatingPost):
    rating_date_epoch_time_seconds:int | None = int(time.time())
    learner_id: str | None = None

class CourseRatingDisplay(CourseRatingBase):
    id:str | None = None
    learner_name:str | None = None
    learner_img:str | None = None