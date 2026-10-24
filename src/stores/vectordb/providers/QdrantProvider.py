from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnums import VectorDBEnum , DistanceMethodEnum
from qdrant_client import QdrantClient , models
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantProvider(VectorDBInterface):
    def __init__(self , db_client:str , default_vector_size:int=786 ,
                  distance_method:str = None , index_threshold:int=100):

        self.db_client = db_client
        self.distance_method = None
        self.client = None
        self.default_vector_size = default_vector_size
        

        if distance_method == DistanceMethodEnum.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnum.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger("uvicorn")

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        if self.client:
            self.client = None

    async def is_collection_existed(self , collection_name:str)->bool:

        if not self.client:
            self.logger.error("Qdrant client was not set")
            return False

        return self.client.collection_exists(collection_name=collection_name)

    async def list_all_collections(self)->List:
        return self.client.get_collections()

    async def get_collection_info(self , collection_name:str)->dict:
        if not self.client:
            self.logger.error("Qdrant client was not set")
            return None

        return self.client.get_collection(collection_name=collection_name)

    async def delete_collection(self , collection_name:str):
        if not self.client:
            self.logger.error("Qdrant client was not set")
            return False
        
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False
        
        self.logger.info(f"Deleting Collection : {collection_name}")
        self.client.delete_collection(collection_name=collection_name)

    async def create_collection(self , collection_name:str , embedding_size:int , do_reset:bool = False):

        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Creating new Qdrant collection :{collection_name}")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),
            )
            return True
        
        return False

    async def insert_one(self , collection_name:str ,text:str, vector:List , metadata:dict = None , record_id:str = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False

        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id = [record_id],
                        vector=vector,
                        payload={
                            "text" : text,
                            "metadata" : metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False
        
        return True

    async def insert_many(self , collection_name:str ,texts:list, vectors:List , metadata:list = None , record_ids:list = None , batch_size:int = 50):

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0 , len(texts)))

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist")
            return False

        for i in range (0 , len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]  

            batch_records = [
                models.Record(
                    id = batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text" : batch_texts[x],
                        "metadata" : batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch records: {e}")
                return False           

        return True

    async def search_by_vector(self , collection_name:str , vector:List , limit : int ):

        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )


        return [
            RetrievedDocument(**{
                "score" : result.score ,
                "text" : result.payload["text"]
            })
            for result in results
        ]
        


