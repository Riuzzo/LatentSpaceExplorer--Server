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
            "model": ErrorModel
        }
    }
)
def get_reductions(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = []
    storage = request.state.storage

    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        user_reductions_dir = 'data-{}'.format(user_id)
        reductions_dir = os.path.join(experiment_dir, user_reductions_dir, constants.REDUCTION_DIR)
    else:
        user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
        experiment_dir = os.path.join(user_dir, experiment_id)
        reductions_dir = os.path.join(experiment_dir, constants.REDUCTION_DIR)

    reductions = []

    try:
        reductions = storage.list(reductions_dir, depth=2)

    except:
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

    for reduction in reductions:
        file_type = reduction.file_type
        file_name = os.path.basename(reduction.path)

        if file_type == 'file' and file_name == constants.METADATA_FILENAME:
            red = {}

            red["id"] = reduction.path.split(os.path.sep)[-2]

            metadata = storage.get_file(reduction.path)
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
    workers = inspector.active().keys()

    for worker_id in workers:
        active = inspector.active().get(worker_id)
        reserved = inspector.reserved().get(worker_id)

        for task in active + reserved:
            if 'reduction' == task['name'] and \
                    experiment_id == task['kwargs']['experiment_id'] and \
                    user_id == task['kwargs']['user_id']:

                response['count'] += 1

    return response


@router.get(
    "/experiments/{experiment_id}/reductions/{reduction_id}",
    tags=["reduction"],
    summary="Get reduction",
    response_model=ReductionModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_reduction(request: Request, experiment_id: str, reduction_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        user_reductions_dir = 'data-{}'.format(user_id)
        reduction_dir = os.path.join(
            experiment_dir, user_reductions_dir, constants.REDUCTION_DIR, reduction_id)
        
    else:
        user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
        experiment_dir = os.path.join(user_dir, experiment_id)
        reduction_dir = os.path.join(
            experiment_dir, constants.REDUCTION_DIR, reduction_id)
    
    
    metadata_path = os.path.join(reduction_dir, constants.METADATA_FILENAME)
    reduction_path = os.path.join(reduction_dir, constants.REDUCTION_FILENAME)
    labels_path = os.path.join(experiment_dir, constants.LABELS_FILENAME)
    print(metadata_path)
    print(reduction_path)
    print(labels_path)
    try:
        metadata = storage.get_file(metadata_path)
        response['metadata'] = json.loads(metadata)

        reduction = storage.get_file(reduction_path)
        response['points'] = json.loads(reduction)

        labels = storage.get_file(labels_path)
        labels = json.loads(labels)
        response['ids'] = labels['columns']

    except:
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

        if not storage.file_exist(labels_path):
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction label file not exist"}
            )

    return response


@router.post(
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
        404: {
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

    try:
        storage.delete(reduction_dir)

    except:
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

    return True
