from fastapi import APIRouter

from src.celery_app.tasks import celery
from src.models.responses.task import TaskModel, TaskCountModel

from celery.states import state, SUCCESS

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

    return response
