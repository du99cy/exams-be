from pydantic import BaseModel

class Transaction(BaseModel):
    id:str | None = None
    amount:int | None = None
    time:str | None = None
    transaction_type:str | None = None
    desc: str |None = None