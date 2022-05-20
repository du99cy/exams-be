from auth.helper_func import get_user_information
from routers.course.helper import get_all_course
from core.database.mongodb import get_collection_client
from ..config import CREDENTIALS_EXCEPTION, TRANSACTION_COLLECTION_NAME,COURSE_COLLECTION_NAME,USER_COLLECTION
from typing import List
from routers.course.model import Course, CourseSummaryInHomePage
from .model import TransactionPost, TransactionSaveToDB
from fastapi import HTTPException
from bson.objectid import ObjectId
async def add_transaction(transaction:TransactionPost,user_id:str):
    #initialize
    paytotal = 0
    order_id = str(ObjectId())
    pay_for_instructor =[] 
    #get collections
    user_collection = await get_collection_client(USER_COLLECTION)
    transaction_collection = await get_collection_client(TRANSACTION_COLLECTION_NAME)
    course_collection = await get_collection_client(COURSE_COLLECTION_NAME)
    #get all course
    course_query = {"is_published": True,"status":2,"id":{"$in":transaction.course_id_list}}
    
    course_list:List[Course] = await get_all_course(course_query)
    
    for course in course_list:
        #check user have been buy this course
        is_bought = await course_collection.find_one({"_id":course.id,"learners_id":{"$in":[user_id]}})
        #if not bought
        if not is_bought:
            paytotal += course.price
            pay_for_instructor.append({"instructor_id": course.instructor_id,"money":course.price})

    #get user information
    user = await get_user_information(user_id)
    
    if user.amount_of_money > paytotal:
        
        #update money for user
        user_collection.update_one({"_id":ObjectId(user_id)},{"$inc":{"amount_of_money":-paytotal}})
       
        #update money for instructor
        for instructor_payment in pay_for_instructor:
            user_collection.update_one({"_id":ObjectId(instructor_payment["instructor_id"])},{"$inc":{"amount_of_money":instructor_payment["money"]}})
        #insert transaction to db
        
        for course in course_list:
             #add user to course
            course_collection.update_one({"id":course.id},{"$push":{"learners_id":user_id}})
            transactionSaveDB = TransactionSaveToDB(**transaction.dict(),customer_id=user_id,course=course,order_id=order_id,money=course.price,instructor_id=course.instructor_id)
            await transaction_collection.insert_one(transactionSaveDB.dict())
    else:
        raise HTTPException(status_code=400,detail="Not enough money")
    

    
async def get_transaction_history_fnc(user_id:str):
    #initialize
    orders = {}
    # get collections
    transaction_collection = await get_collection_client(TRANSACTION_COLLECTION_NAME)

    transaction_list_cursor = transaction_collection.find({"customer_id":user_id})

    async for transaction in transaction_list_cursor:
        transaction["id"] = str(transaction["_id"])
        del transaction["_id"]
        orders.setdefault(transaction["order_id"],[])
        orders[transaction["order_id"]].append(transaction)

    return orders


async def get_best_seller_func(user_id:str):
    best_seller_list = []
    #get collection
    transaction_collection = await get_collection_client(TRANSACTION_COLLECTION_NAME)
    user_collection = await get_collection_client(USER_COLLECTION)
    
    #get user information
    user = await get_user_information(user_id)
    # if user.role_id !=1:
    #     raise CREDENTIALS_EXCEPTION
    result = transaction_collection.aggregate([{"$group":{"_id":{"course_id":"$course.id","title":"$course.title","img":"$course.img_name","category":"$course.category","price":"$course.price"},"count":{"$sum":1}}}])
    async for r in result:
        best_seller_list.append(r)
    return best_seller_list