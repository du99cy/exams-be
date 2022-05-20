
from fastapi import FastAPI,Request,Response
import uvicorn
import os
from auth.router import api_router as AuthRouter
from core.database.mongodb import connect_db,close_db
from fastapi.middleware.cors import CORSMiddleware
from routers import api_router_list
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
# from fastapi_redis_cache import FastApiRedisCache, cache
app = FastAPI()

#add startup and shutdown event
app.add_event_handler("startup",connect_db)
app.add_event_handler("shutdown",close_db)
#add auth router
app.include_router(AuthRouter)
#add routers list

LOCAL_REDIS_URL = "redis://127.0.0.1:6379"

for router in api_router_list:
    app.include_router(router["name"])

#CORS
origins = [
    "https://localhost:4300",
    "http://localhost:4300",
    "http://45.77.245.61:9920",
    "http://localhost:4200",
    "https://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#compress response from server
app.add_middleware(GZipMiddleware, minimum_size=1000)
#mounting static file resourse
app.mount("/static-files", StaticFiles(directory="static-files"), name="staticFile")

# @app.on_event("startup")
# def startup():
#     redis_cache = FastApiRedisCache()
#     redis_cache.init(
#         host_url=os.environ.get("REDIS_URL", LOCAL_REDIS_URL),
#         prefix="eduvn-cache",
#         response_header="EduVN-Cache",
#         ignore_arg_types=[Request, Response]
#     )

if __name__ == '__main__':
    uvicorn.run("main:app",host='0.0.0.0',port=9920,reload=True)
    
