from core.database.mongodb import get_collection_client
from ..config import RECHARGE_HISTORY_COLLECTION_NAME
async def get_recharge_history_of_user_helper(user_id:str):
    #initialize
    recharge_history_list = []
    #get collections
    recharge_history_collection = await get_collection_client(RECHARGE_HISTORY_COLLECTION_NAME)

    recharge_history_list_cursor = recharge_history_collection.find({"user_id":user_id})

    async for recharge_his in recharge_history_list_cursor:
        recharge_his["id"] = str(recharge_his["_id"])
        del recharge_his["_id"]
    
        recharge_history_list.append(recharge_his)
    return recharge_history_list

