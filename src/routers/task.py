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


@router.get(
    "/tasks/reduction/pending",
    tags=["tasks"],
    summary="Get reduction's tasks in pending status",
    response_model=TaskCountModel
)
def get_reduction_task_in_pending():
    response = {}
    inspector = celery.control.inspect()
    celery_servers = inspector.active().keys()

    response['count'] = 0
    for server_id in celery_servers:
        server = inspector.active().get(server_id)
        for task in server:
            if task['name'] == 'reduction':
                response['count'] += 1

    return response


@router.get(
    "/tasks/cluster/pending",
    tags=["tasks"],
    summary="Get cluster's tasks in pending status",
    response_model=TaskCountModel
)
def get_reduction_task_in_pending():
    response = {}
    inspector = celery.control.inspect()
    celery_servers = inspector.active().keys()

    response['count'] = 0
    for server_id in celery_servers:
        server = inspector.active().get(server_id)
        for task in server:
            if task['name'] == 'cluster':
                response['count'] += 1

    return response
