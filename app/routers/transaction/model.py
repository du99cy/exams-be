from pydantic import BaseModel
from typing import List
import time

from routers.course.model import Course

class TransactionBase(BaseModel):
    created_at:int | None = int(time.time())
    transaction_type:str | None = 1
    #transaction type 1:course purchase
    customer_id:str | None = None
    status:int | None =1
    #stutus 1:success
class TransactionPost(BaseModel):
    course_id_list:List[str]| None = []
       
class Transaction(TransactionPost):
    id:str | None = None

class TransactionSaveToDB(TransactionBase):
    course:Course | None = None
    order_id:str | None = None
    instructor_id: str | None = None
    money: float | None = None


    



    