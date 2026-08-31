from fastapi import APIRouter, Depends, UploadFile , status
from fastapi.responses import JSONResponse
from src.controllers import DataController , ProjectController , ProcessController
from src.helpers.config import Settings, get_settings
import os
import aiofiles
from src.models.Enums.response_enums import ResponseEnums
import logging 
from .schemes.data import ProcessRequest 
logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix= "/api/v1/data",
    tags=["data","api_v1"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id : str , file : UploadFile , app_settings : Settings = Depends(get_settings)):


            is_valid , message = DataController().validate_uploaded_file(file=file)

            if is_valid is False:
                    return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal" : message 
                            } 
                    )

            project_dir_path = ProjectController().get_project_path(project_id=project_id)
            file_path , file_id = DataController().generate_unique_filepath(original_filename=file.filename , project_id=project_id)

            try:
                async with aiofiles.open(file_path, 'wb') as f:
                        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                            await f.write(chunk)
            except Exception as e:
                logger.error(f"An error occurred while uploading the file: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "signal" : ResponseEnums.FILE_UPLOAD_FAILED.value,
                    }
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "signal" : message,
                    "and file_id" : file_id
                }
            )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id : str , process_request : ProcessRequest):

       file_id = process_request.file_id

       process_controller = ProcessController(project_id=project_id)
       file_content = process_controller.get_file_content(file_id=file_id)
       file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=process_request.chunk_size,
            overlap_size=process_request.overlap_size
            )

       if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseEnums.PROCESSING_FAILED.value,
                }
            )
       return file_chunks