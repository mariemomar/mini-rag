from typing import Optional
from pydantic import BaseModel , Field , validator  #data validation and settings management
from bson import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id : ObjectId

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key" : [("chunk_project_id" , 1)], # 1 means ascending order
                "name" : "chunk_project_id_index_1",
                "unique" : False
            }
        ]

    class Config:
        arbitrary_types_allowed = True


class RetrievedDocument(BaseModel): # a new schema for the retrieved results
    text : str
    score : float