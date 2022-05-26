import datetime
from gzip import READ
from fastapi import APIRouter, Body, Request, Path,Depends
from bson.objectid import ObjectId
from core.constants import VNPAY_HASH_SECRET_KEY, VNPAY_PAYMENT_URL, VNPAY_RETURN_URL, VNPAY_TMN_CODE, LANGUAGE, ORDER_TYPE

from core.helpers_func import responseModel
from routers.recharge.model import Recharge, vnpay
from core.database.mongodb import get_collection_client
from auth.dependencies import get_current_active_user
from .helper import get_recharge_history_of_user_helper 
from ..config import RECHARGE_HISTORY_COLLECTION_NAME, USER_COLLECTION
api_router = APIRouter(tags = ['Recharge'],prefix='/recharge')

@api_router.post('')
async def payment(request: Request, recharge: Recharge = Body(...)):
    
    order_type = ORDER_TYPE
    order_id = recharge.order_id
    amount = recharge.amount
    order_desc = 'Nap tien ngay: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bank_code = recharge.bank_code
    language = LANGUAGE
    ipaddr = request.client.host
    # Build URL Payment
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = int(amount)
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = order_id
    vnp.requestData['vnp_OrderInfo'] = order_desc
    vnp.requestData['vnp_OrderType'] = order_type
    # Check language, default: vn
    if language and language != '':
        vnp.requestData['vnp_Locale'] = language
    else:
        vnp.requestData['vnp_Locale'] = 'vn'
        # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
    if bank_code and bank_code != "":
        vnp.requestData['vnp_BankCode'] = bank_code

    vnp.requestData['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
    vnp.requestData['vnp_IpAddr'] = ipaddr
    vnp.requestData['vnp_ReturnUrl'] = VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(VNPAY_PAYMENT_URL, VNPAY_HASH_SECRET_KEY)
    
    return responseModel(data=vnpay_payment_url)


@api_router.post('/ipn')
async def postIPN(order = Body(...),current_user=Depends(get_current_active_user)):
    
    vnp = vnpay()
    vnp.responseData = order
    order["vnp_Amount"] =  int(order["vnp_Amount"])
    vnp_ResponseCode = order['vnp_ResponseCode']
    if vnp.validate_response(VNPAY_HASH_SECRET_KEY):
    # Check & Update Order Status in your Database
    # Your code here
        firstTimeUpdate = True
        totalamount = True
        if totalamount:
            if firstTimeUpdate:
                if vnp_ResponseCode == '00':
                    print('Payment Success. Your code implement here')
                else:
                    print('Payment Error. Your code implement here')

                # Return VNPAY: Merchant update success
                result = {'RspCode': '00', 'Message': 'Nạp tiền thành công'}
            else:
                # Already Update
                result = {'RspCode': '02', 'Message': 'Giao dịch đã được cập nhật'}
        else:
                # invalid amount
            result = {'RspCode': '04', 'Message': 'Số tiền không hợp lệ'}
    else:
        # Invalid Signature
        result = {'RspCode': '97', 'Message': 'Chữ ký không hợp lệ'}

    #get collections
    recharge_history_collection = await get_collection_client(RECHARGE_HISTORY_COLLECTION_NAME)
    user_collection = await get_collection_client(USER_COLLECTION)
    #since order is dict
    order.update({"user_id":current_user.id})
    #check whether transaction is exists or not
    transaction_exists = await recharge_history_collection.find_one({"vnp_BankTranNo":order["vnp_BankTranNo"]})
    if transaction_exists:
        result={"RspCode":'05',"Message":"Giao dịch đã thực hiện"}
    else:
        
        await recharge_history_collection.insert_one(order)
        #update to amount of money to user
        await user_collection.update_one({"_id":ObjectId(current_user.id)},{"$inc":{"amount_of_money":float(order["vnp_Amount"])}})
    return responseModel(data = result)

@api_router.get("")
async def get_recharge_history_of_user(current_user=Depends(get_current_active_user)):
    recharge_history_list = await get_recharge_history_of_user_helper(current_user.id)
    return responseModel(data=recharge_history_list)