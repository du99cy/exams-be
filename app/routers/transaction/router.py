from calendar import c
from gzip import READ

from fastapi import APIRouter, Body, HTTPException,Path,Depends

from routers.config import COURSE_COLLECTION_NAME, CREDENTIALS_EXCEPTION, TRANSACTION_COLLECTION_NAME, USER_COLLECTION
from core.database.mongodb import get_collection_client
from core.helpers_func import responseModel
from routers.transaction.model import Transaction, TransactionPost
from auth.dependencies import get_current_active_user
from auth.helper_func import get_user_information
from .helper import add_transaction, get_transaction_history_fnc
from bson.objectid import ObjectId
import time
api_router = APIRouter(tags = ['Transaction'],prefix='/transaction')
@api_router.post('')
async def createOrder(transaction:TransactionPost = Body(...),current_user=Depends(get_current_active_user)):
   
    await add_transaction(transaction,current_user.id)
    return responseModel()

@api_router.get("")
async def get_transaction_history(current_user = Depends(get_current_active_user)):
    transaction_his = await get_transaction_history_fnc(current_user.id)
    return responseModel(data = transaction_his)

#cannot get amount of money from token because token contain user information that not updated yet
# since when I update user information in FE and DB but still use the same token ,but that token not updated
# unless I recreate token then have new token that have user information update

