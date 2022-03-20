from re import T
from ..constants import MONGO_DETAILS,DATABASE_NAME
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorCollection


db_client: AsyncIOMotorClient = AsyncIOMotorClient()

async def connect_db():
    """Create database connection."""
    global db_client
    db_client = AsyncIOMotorClient(MONGO_DETAILS)

async def close_db():
    """Close database connection."""
    db_client.close()
    
async def get_collection_client(collection_name:str, database_name:str = DATABASE_NAME)->AsyncIOMotorCollection:
    global db_client
    """Return database client instance."""
    return db_client[database_name][collection_name]



    
