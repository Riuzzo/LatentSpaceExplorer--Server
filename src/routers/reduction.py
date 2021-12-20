import os
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import Union, List

from src.celery_app import tasks
from src.models.requests.reduction import PCAModel, TSNEModel, UMAPModel, TruncatedSVDModel, SpectralEmbeddingModel, IsomapModel, MDSModel
from src.models.responses.reduction import ReductionBaseModel, ReductionModel, ReductionPendingModel
from src.models.responses.task import TaskBaseModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization


router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/reductions",
    tags=["reduction"],
    summary="Get reductions",
    response_model=List[ReductionBaseModel],
    responses={
        404: {
            "description": "Reduction not found",
            "model": ErrorModel
        }
    }
)
def get_reductions(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    reductions_dir = os.path.join(experiment_dir, constants.REDUCTION_DIR)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.dir_exist(reductions_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Reductions dir not valid"}
        )

    reductions = storage.list(reductions_dir)

    for reduction in reductions:
        if reduction.file_type == 'dir':
            red = {}
            red["id"] = reduction.name

            metadata_path = os.path.join(
                reduction.path, constants.METADATA_FILENAME)

            if storage.file_exist(metadata_path):
                metadata = storage.get_file(metadata_path)
                red['metadata'] = json.loads(metadata)
                response.append(red)

    return response


@router.get(
    "/experiments/{experiment_id}/reductions/pending",
    tags=["reduction"],
    summary="Get pending reductions count",
    response_model=ReductionPendingModel,
)
def get_pending_reductions_count(experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    response['count'] = 0

    inspector = tasks.celery.control.inspect()
    celery_servers = inspector.active().keys()

    for server_id in celery_servers:
        server = inspector.active().get(server_id)

        for task in server:
            if 'reduction' == task['name'] and \
                    experiment_id == task['kwargs']['experiment_id'] and \
                    user_id == task['kwargs']['user_id']:

                response['count'] += 1

    return response


@ router.get(
    "/experiments/{experiment_id}/reductions/{reduction_id}",
    tags=["reduction"],
    summary="Get reduction",
    response_model=ReductionModel,
    responses={
        404: {
            "description": "Reduction not found",
            "model": ErrorModel
        }
    }
)
def get_reduction(request: Request, experiment_id: str, reduction_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    reduction_dir = os.path.join(
        experiment_dir, constants.REDUCTION_DIR, reduction_id)
    metadata_path = os.path.join(reduction_dir, constants.METADATA_FILENAME)
    reduction_path = os.path.join(reduction_dir, constants.REDUCTION_FILENAME)
    ids_path = os.path.join(experiment_dir, constants.IDS_FILENAME)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.dir_exist(reduction_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction id not valid"}
        )

    if not storage.file_exist(metadata_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction metadata file not exist"}
        )

    if not storage.file_exist(reduction_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction file not exist"}
        )

    if not storage.file_exist(ids_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction label file not exist"}
        )

    metadata = storage.get_file(metadata_path)
    response['metadata'] = json.loads(metadata)

    reduction = storage.get_file(reduction_path)
    response['points'] = json.loads(reduction)

    ids = storage.get_file(ids_path)
    ids = json.loads(ids)
    response['ids'] = ids

    return response


@ router.post(
    "/experiments/{experiment_id}/reductions",
    tags=["reduction"],
    summary="Create new reduction",
    response_model=TaskBaseModel,
    status_code=201
)
def post_reduction(
    request: Request,
    reduction: Union[PCAModel, TSNEModel, UMAPModel, TruncatedSVDModel, SpectralEmbeddingModel, IsomapModel, MDSModel],
    experiment_id: str, user_id: dict = Depends(authorization)
):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    # task = tasks.reduction.delay(
    task = tasks.reduction.apply_async(
        kwargs={
            "algorithm": reduction.algorithm,
            "components": reduction.components,
            "params": reduction.params.dict(),
            "experiment_id": experiment_id,
            "user_id": user_id
        }
    )

    response['task_id'] = task.id

    return response


@router.delete(
    "/experiments/{experiment_id}/reductions/{reduction_id}",
    tags=["reduction"],
    summary="Delete reduction",
    responses={
        200: {
            "description": "Reduction deleted",
        },
        404: {
            "description": "Reduction not found",
            "model": ErrorModel
        }
    }
)
def delete_reduction(request: Request, experiment_id: str, reduction_id: str, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    reduction_dir = os.path.join(
        experiment_dir, constants.REDUCTION_DIR, reduction_id)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": "Experiment id not valid"}
        )

    if not storage.dir_exist(reduction_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": "Reduction id not valid"}
        )

    storage.delete(reduction_dir)

    return True
