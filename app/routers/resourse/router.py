from fastapi import APIRouter, File, UploadFile
from core.helpers_func import responseModel
import aiofiles

api_router = APIRouter(tags=["Resourse"],prefix="/resourse")

@api_router.post("/uploadFile")
async def uploadFile(file:UploadFile= File(...)):
    out_file = f"file/{file.filename}"
    async with aiofiles.open(out_file, 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return {"Result": "OK"}