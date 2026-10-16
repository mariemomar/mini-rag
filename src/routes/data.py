from controllers import process_controller
from fastapi import APIRouter, Depends, UploadFile , status, Request
from fastapi.responses import JSONResponse
from src.controllers import DataController , ProjectController , ProcessController
from src.helpers.config import Settings, get_settings
import os
import aiofiles
from src.models.Enums.response_enums import ResponseEnums 
from models.Enums.AssetTypeEnum import AssetTypeEnum 
import logging 
from .schemes.data import ProcessRequest 
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset



logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix= "/api/v1/data",
    tags=["data","api_v1"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(request : Request , project_id : int , file : UploadFile , app_settings : Settings = Depends(get_settings)):

            project_model = await ProjectModel.create_instance(
                   db_client = request.app.db_client,
            )
            project = await project_model.get_project_or_create_one(project_id=project_id)
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

            asset_model = await AssetModel.create_instance(
                db_client = request.app.db_client,
            )
            asset_resource = Asset(
                asset_project_id=project.project_id,
                asset_type=AssetTypeEnum.FILE.value,
                asset_name=file_id,
                asset_size=os.path.getsize(file_path),
            )

            asset_record = await asset_model.create_asset(asset=asset_resource)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "signal" : message,
                    "file_id" : str(asset_record.asset_id) ,
                }
            )


@data_router.post("/process/{project_id}")
async def process_endpoint(request : Request , project_id : int , process_request : ProcessRequest):

    


    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client,
        )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    asset_model = await AssetModel.create_instance(
            db_client = request.app.db_client,
        )

    
    project_files_ids = {} 
    if process_request.file_id: # in case user entered the file id
        asset_record = await asset_model.get_asset_record(
             asset_project_id=project.project_id , asset_name=process_request.file_id
             )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseEnums.FILE_ID_ERROR.value,
                }
            )
        project_files_ids = {
             asset_record.asset_id : asset_record.asset_name
        }

    else : # user did not enter the file id 
        
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.project_id , asset_type=AssetTypeEnum.FILE.value)
        project_files_ids = {
             record.asset_id : record.asset_name
             for record in project_files
        }
        if len(project_files_ids) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseEnums.NO_FILES_ERROR.value,
                }
            )

    process_controller = ProcessController(project_id=project_id)
    no_records = 0 
    no_files =  0

    chunk_model = await ChunkModel.create_instance(
            db_client = request.app.db_client,
        )

    if do_reset == 1:
        _= await chunk_model.delete_chunks_by_project_id(project_id=project.project_id)

    for asset_id , file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)
        if file_content is None or len(file_content) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal" : ResponseEnums.FILE_CONTENT_EMPTY.value,
                }
            )
        file_chunks = process_controller.process_file_content(
                file_content=file_content,
                file_id=file_id,
                chunk_size=process_request.chunk_size,
                overlap_size=process_request.overlap_size
                )
            
        if file_chunks is None:
                logger.error(f"Error while processing file: {file_id}")
                continue  # Skip to the next file if processing fails

        file_chunks_records = [
                DataChunk(
                        
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order= i + 1,
                    chunk_project_id=project.project_id,
                    chunk_asset_id= asset_id
                )
                for i , chunk in enumerate(file_chunks)
        ]

        

        no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_files += 1
        
    return JSONResponse(
            content={
                "signal" : ResponseEnums.PROCESSING_SUCCEEDED.value,
                "inserted_chunks" : no_records,
                "processed_files" : no_files
            }
        )