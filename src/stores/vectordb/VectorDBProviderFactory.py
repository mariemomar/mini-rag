from .providers import QdrantProvider , PGVectorProvider
from .VectorDBEnums import VectorDBEnum , PgVectorDistanceMethodEnums
from controllers.base_controller import BaseController
from sqlalchemy.orm import sessionmaker


class VectorDBProviderFactory:
    def __init__(self , config:dict , db_client:sessionmaker = None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client

    def create(self , provider:str):
        if provider == VectorDBEnum.QDRANT.value:

            qdrant_db_client = self.base_controller.get_database_path(database_name = self.config.VECTOR_DB_PATH)

            return QdrantProvider(
                db_client = qdrant_db_client,
                distance_method = self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEG_INDEX_THRESHOLD

            )

        if provider == VectorDBEnum.PGVECTOR.value:
        
           return PGVectorProvider(
               db_client= self.db_client,
               default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
               distance_method=PgVectorDistanceMethodEnums.COSINE.value,
               index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
           )

        return None
        