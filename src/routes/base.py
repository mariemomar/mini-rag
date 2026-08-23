from fastapi import FastAPI , APIRouter , Depends # it is important for the function that depends on the app settings 
from helpers.config import get_settings , Settings
base_router = APIRouter(
    prefix= "/api/v1",
    tags=["api_v1"]
)

# do function of welocome 

@base_router.get("/")
async def welcome(app_settings : Settings = Depends(get_settings)):
    # app_settings = get_settings()
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name" : app_name,
        "app_version" : app_version
    }
