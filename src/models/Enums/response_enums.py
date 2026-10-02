from enum import Enum

class ResponseEnums(Enum):
    FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
    FAILURE = "failure"
    FILE_TYPE_NOT_ALLOWED ="File type not allowed"
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds limit"
    FILE_UPLOAD_FAILED = "File upload failed"
    PROCESSING_FAILED = "File processing failed"
    PROCESSING_SUCCEEDED = "File processing succeeded"
    NO_FILES_FOUND_FOR_PROCESSING = "No files found for processing"
    NO_FILES_ERROR = "not_found_files"
    FILE_ID_ERROR = "no_file_found_with_this_id"