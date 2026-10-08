from fastapi import FastAPI
from src.routes import data, base , nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser


app = FastAPI()

@app.on_event("startup")
async def startup_span():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_providers_factory = LLMProviderFactory(settings)
    vectordb_providers_factory = VectorDBProviderFactory(settings)

    # generation client 
    app.generation_client = llm_providers_factory.create(provider = settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # embedding client 
    app.embedding_client = llm_providers_factory.create(provider = settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID , settings.EMBEDDING_MODEL_SIZE)

    # vector database client
    app.vectordb_client = vectordb_providers_factory.create(provider = settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    # template parser
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANG , default_language  =settings.DEFAULT_LANG)

@app.on_event("shutdown")
async def shutdown_span():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()


# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
