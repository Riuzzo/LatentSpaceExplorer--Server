from fastapi import APIRouter

from src.celery_app import tasks
from src.celery_app.tasks import celery
from src.models.responses.task import TaskModel

from celery.states import state, SUCCESS

router = APIRouter()

@router.get(
    "/queue/{task_id}",
    tags=["queue"],
    summary="Get task info. If the task is completed, return the result.",
    response_model=TaskModel
)
def get_task_status(task_id):
    response = {}
    response['task_id'] = task_id
    task = celery.AsyncResult(task_id)
    
    response['status'] = task.state
    if task.state == state(SUCCESS):
        response['name'] = task.name
        response['result_id'] = task.get()
    return response
