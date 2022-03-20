
from fastapi import FastAPI
import uvicorn
from auth.router import api_router as AuthRouter
from core.database.mongodb import connect_db,close_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#add startup and shutdown event
app.add_event_handler("startup",connect_db)
app.add_event_handler("shutdown",close_db)

app.include_router(AuthRouter)

#CORS

origins = [
    
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    uvicorn.run("main:app",host='127.0.0.1',port=8000,reload=True)