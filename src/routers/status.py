import os
import redis
import time

from fastapi import APIRouter

from src.celery_app.tasks import celery
from src.models.responses.status import StatusModel

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()


@router.get(
    "/status",
    tags=["status"],
    summary="Get task",
    response_model=StatusModel
)
def get_status():
    total_time = time.time()
    response = {}

    # server
    response['server'] = True

    # queue
    redis_host = os.environ.get("REDIS_QUEUE_SERVICE_HOST")
    redis_port = os.environ.get("REDIS_QUEUE_SERVICE_PORT")
    queue = redis.Redis(host=redis_host, port=redis_port, db=0)
    response['queue'] = queue.ping()

    # scheduler
    inspect = celery.control.inspect()
    workers = inspect.stats()
    response['scheduler'] = len(workers.keys()) > 0

    elapsed = time.time() - total_time
    logger.info(message='Get status', action='get_status', status='SUCCESS', resource='lse-service', duration=elapsed)

    return response
