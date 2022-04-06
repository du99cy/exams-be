from fastapi import APIRouter, File, UploadFile,Depends
from auth.dependencies import get_current_active_user

api_router = APIRouter(tags=["Test"],prefix="/test")

@api_router.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(..., description="A file read as UploadFile")
):
    
    return {"file":file}

@api_router.get("/test_auth")
async def test_auth(current_user=Depends(get_current_active_user)):
    return current_user.dict()
    