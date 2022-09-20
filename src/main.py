import os
import time
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.encoders import jsonable_encoder

# server
import uvicorn
from fastapi import FastAPI, Request
from fastapi import status as HTTPCodes
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# routers
from src.routers import experiment, reduction, cluster, label, task, image, status

# other
from src.utils.storage import Storage
from src.utils.authorization import AuthError

# logging
import logging
import structlog
from pythonjsonlogger import jsonlogger

### LOGGING CONFIGURATION


#logger.info(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.warning(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.debug(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.accounting(message='Posted cluster task', action='Clustering', value=1, measue="unit", resource='lse', userid=user_id)

# Extending structlogger with custom level 'accounting'
ACCOUNTING = 15    # set to random value between DEBUG and INFO

structlog.stdlib.ACCOUNTING = ACCOUNTING
structlog.stdlib._NAME_TO_LEVEL['accounting'] = ACCOUNTING
structlog.stdlib._LEVEL_TO_NAME[ACCOUNTING] = 'accounting'

def accounting(self, *args, **kw):
    return self.log(ACCOUNTING, *args, **kw)

structlog.stdlib._FixedFindCallerLogger.accounting = accounting
structlog.stdlib.BoundLogger.accounting = accounting

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter())

logger = structlog.getLogger("json_logger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(handler)

# environment
load_dotenv()

storage = Storage(host=os.getenv('NEXCLOUD_HOST'))
app = FastAPI(root_path=os.getenv('APP_SERVER_ROOT_PATH'))


# CORS middleware
# origins = [
#     "http://lse.local",
#     "https://lse.staging.neanias.eu",
#     "https://lse.neanias.eu"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
        status_code=HTTPCodes.HTTP_401_UNAUTHORIZED,
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
        status_code=HTTPCodes.HTTP_422_UNPROCESSABLE_ENTITY,
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
app.include_router(status.router)


# startup event
@app.on_event("startup")
async def startup():
    initial_time = time.time()
    storage.connect(
        user=os.getenv('NEXCLOUD_USER'),
        password=os.getenv('NEXCLOUD_PASSWORD'),
    )
    elapsed = time.time() - initial_time
    #Add time elapsed to the log?
    logger.info(message='Storage client connected to nextcloud', duration=elapsed, action='storage_client_connected', resource='lse-service', userid="Server")


# shutdown event
@app.on_event("shutdown")
async def shutdown():
    storage.disconnect()
    logger.info(message='Storage client disconnected from nextcloud', action='storage_client_disconnected', resource='lse-service', userid="Server")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv('APP_SERVER_HOST'),
        port=int(os.getenv('APP_SERVER_PORT')),
        reload=os.getenv('APP_SERVER_RELOAD')
    )
