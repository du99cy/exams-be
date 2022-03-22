from fastapi import APIRouter, File, UploadFile

api_router = APIRouter(tags=["Test"],prefix="/test")

@api_router.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(..., description="A file read as UploadFile")
):
    
    return {"file":file}