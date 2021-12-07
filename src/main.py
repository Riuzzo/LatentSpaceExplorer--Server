import os
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# server
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# routers
from src.routers import experiment, reduction, cluster, task, image

# other
from utils.storage import Storage


# environment
load_dotenv()
load_dotenv(os.getenv('ENVIRONMENT_FILE'))

storage = Storage(host=os.getenv('NEXCLOUD_HOST'))
app = FastAPI(root_path=os.getenv('APP_SERVER_ROOT_PATH'))


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# storage middleware
@app.middleware("http")
async def storage_middleware(request: Request, call_next):
    request.state.storage = storage

    try:
        return await call_next(request)

    except HTTPException as exception:
        return JSONResponse(status_code=exception.status_code, content=exception.detail)


# routers
app.include_router(experiment.router)
app.include_router(reduction.router)
app.include_router(cluster.router)
app.include_router(task.router)
app.include_router(image.router)


# startup event
@app.on_event("startup")
async def startup():
    storage.connect(
        user=os.getenv('NEXCLOUD_USER'),
        password=os.getenv('NEXCLOUD_PASSWORD'),
    )


# shutdown event
@app.on_event("shutdown")
async def shutdown():
    storage.disconnect()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv('APP_SERVER_HOST'),
        port=int(os.getenv('APP_SERVER_PORT')),
        reload=os.getenv('APP_SERVER_RELOAD')
    )
