from gzip import READ
from fastapi import APIRouter, Body, HTTPException
from routers.config import TRANSACTION_COLLECTION_NAME
from core.database.mongodb import get_collection_client
from core.helpers_func import responseModel
from routers.transaction.model import Transaction
api_router = APIRouter(tags = ['Transaction'],prefix='/transaction')
@api_router.post('')
async def createOrder(transaction: Transaction = Body(...)):
    transaction_collection = await get_collection_client(TRANSACTION_COLLECTION_NAME)
    # check document exists
    course_exists = await transaction_collection.find_one({"id": transaction.id})
    if course_exists:
        raise HTTPException(
            status_code=400, detail="have been exists course in system")
    # transaction_dict = transaction_collection.dict()

    # add to mongodb
    result = await transaction_collection.insert_one(transaction_collection)
    return responseModel(status_code=200) if result else None