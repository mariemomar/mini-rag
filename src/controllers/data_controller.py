from src.controllers.base_controller import BaseController
from src.models.Enums.response_enums import ResponseEnums
from fastapi import UploadFile
from src.controllers.project_controller import ProjectController
import re
import os 

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # 1 MB in bytes

    def validate_uploaded_file(self , file : UploadFile):
        
        allowed_types = self.app_settings.FILE_ALLOWED_TYPES
        if file.content_type not in allowed_types:
            return False , ResponseEnums.FILE_TYPE_NOT_ALLOWED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False , ResponseEnums.FILE_SIZE_EXCEEDS_LIMIT.value
        return True , ResponseEnums.FILE_UPLOADED_SUCCESSFULLY.value  

    def generate_unique_filepath(self, original_filename: str , project_id: str) -> str:

        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_filename = self.get_clean_file_name(original_filename)

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_filename
        )
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_filename
            )
        return new_file_path , random_key + "_" + cleaned_filename


    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name