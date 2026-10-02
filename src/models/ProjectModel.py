from .BaseDataModel import BaseDataModel
from .db_schemes import Project 
from .Enums.DatabaseEnum import DatabaseEnum  

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_conllection()
        return instance

    async def init_conllection(self):

        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                    )

    async def create_project(self, project: Project):
        """
        Create a new project in the database.
        """
        result = await self.collection.insert_one(project.dict(by_alias=True , exclude_unset=True)) # project is pydantic model so we convert it to dict before inserting
        project.id = result.inserted_id  # Update the project instance with the generated ObjectId
        return project

    async def get_project_or_create_one(self, project_id: str):

        record = await self.collection.find_one({"project_id" : project_id})
        if record: # return it as pydantic 
            return Project(**record)
        if record is None:
            new_project = Project(project_id=project_id)
            return await self.create_project(new_project) # await because create_project is an async function

    async def get_all_projects(self , page: int = 1 , page_size : int = 10 ): # do not use get all without pagination in production

        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size + (1 if total_documents % page_size > 0 else 0)

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = [Project(**doc) async for doc in cursor]  # Convert each document
        return projects, total_pages