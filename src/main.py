import os
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.encoders import jsonable_encoder

# server
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# routers
from src.routers import experiment, reduction, cluster, label, task, image

# other
from src.utils.storage import Storage
from src.utils.authorization import AuthError


# environment
load_dotenv()
load_dotenv(os.getenv('ENVIRONMENT_FILE'))

storage = Storage(host=os.getenv('NEXCLOUD_HOST'))
app = FastAPI(root_path=os.getenv('APP_SERVER_ROOT_PATH'))


# CORS middleware
origins = [
    "http://lse.local",
    "https://lse.staging.neanias.eu",
    "https://lse.neanias.eu"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
        print('storage middleware:\n\t{}'.format(exception.errors()))
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                {
                    "detail": exception.errors(),
                    "message": "An error occurred with storage middleware"
                }
            ),
        )


@app.exception_handler(AuthError)
async def authorizatrion_handler(request: Request, exc: AuthError):
    print('authorizatrion middleware:\n\t{}'.format(exc.user_id))
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=jsonable_encoder(
            {
                "detail": "The user id {} not exist".format(exc.user_id),
                "message": "User directory not exist"
            }
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print('validation middleware:\n\t{}'.format(exc.errors()))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "detail": exc.errors(),
                "message": "An error occurred on validating the request parameters"
            }
        ),
    )


# @app.exception_handler(ValueError)
# async def value_error_exception_handler(request: Request, exc: ValueError):
#     print('value error middleware:\n\t{}'.format(exc.errors()))
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content=jsonable_encoder(
#             {
#                 "detail": exc.errors(),
#                 "message": "Internal Server Error"
#             }
#         )
#     )


# routers
app.include_router(experiment.router)
app.include_router(reduction.router)
app.include_router(cluster.router)
app.include_router(label.router)
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
