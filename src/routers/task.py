from fastapi import APIRouter

from celery_app.tasks import celery
from models.responses.task import TaskModel

from celery.states import state, SUCCESS

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()


@router.get(
    "/tasks/{task_id}",
    tags=["tasks"],
    summary="Get task",
    response_model=TaskModel
)
def get_task(task_id):
    response = {}
    response['task_id'] = task_id

    task = celery.AsyncResult(task_id)

    response['status'] = task.state

    if task.state == state(SUCCESS):
        response['name'] = task.name
        response['result_id'] = task.get()

    logger.info(message='Get task', action='get_task', status='SUCCESS', resource='lse-service')

    return response
