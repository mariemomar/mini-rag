from fastapi import FastAPI , APIRouter , Depends , UploadFile # it is important for the function that depends on the app settings 
from helpers.config import get_settings , Settings


data_router = APIRouter(
    prefix= "/api/v1/data",
    tags=["data","api_v1"]
)

@data_router.post("upload/{project_id}")
def upload_file(project_id : str , file : UploadFile , 
                app_settings : Settings = Depends(get_settings)):

    # uploading file properties  (this is a logic so we can do it in another place and just call it here) {controllers}



