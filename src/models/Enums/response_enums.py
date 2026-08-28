from enum import Enum

class ResponseEnums(Enum):
    FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
    FAILURE = "failure"
    FILE_TYPE_NOT_ALLOWED ="File type not allowed"
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds limit"
    FILE_UPLOAD_FAILED = "File upload failed"