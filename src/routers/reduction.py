import os
import owncloud

from fastapi import APIRouter, Header, Request, Depends
from fastapi.responses import JSONResponse
from typing import Union, List

from src.celery_app import tasks
from src.models.requests.reduction import PCAModel, TSNEModel, UMAPModel
from src.models.responses.reduction import MetadataReductionModel, ReductionModel
from src.models.responses.task import MetadataTaskModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

import json

router = APIRouter()

@router.get(
    "/experiments/{experiment_id}/reductions",
    tags=["reduction"],
    summary="Get all reduction's metadata",
    response_model=List[MetadataReductionModel]
)
def get_all_reductions( experiment_id: str, request: Request, user_id: dict = Depends(authorization)):
    response = []

    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    path = os.path.join(data_dir, experiment_id, constants.REDUCTION_DIR)
    
    try:
        reductions = storage.list(path, depth=1)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment doesn't exist"}
        )
    
    for red in reductions:
        if red.file_type == 'dir':
            record = {}
            record["id"] = red.name
            path = os.path.join(red.path, constants.METADATA_FILENAME)
            try:
                record['metadata'] = json.loads(storage.get_file(path))
                response.append(record)

            except owncloud.owncloud.HTTPResponseError:
                pass # If the file is deleted, don't add it to the list
    
    return response


@router.get(
    "/experiments/{experiment_id}/reductions/{reduction_id}",
    tags=["reduction"],
    summary="Get reduction result",
    response_model=ReductionModel,
    responses={
        404: {
            "description": "Reduction not found",
            "model": ErrorModel
        }   
    }
)
def get_single_reduction(experiment_id: str, reduction_id: str, request: Request, user_id: dict = Depends(authorization)):
    response = {}
    
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    experiment_path = os.path.join(data_dir, experiment_id)
    reduction_path = os.path.join(data_dir, experiment_id, constants.REDUCTION_DIR, reduction_id)

    metadata_file = os.path.join(reduction_path, constants.METADATA_FILENAME)
    labels_file = os.path.join(experiment_path, constants.LABELS_FILENAME)
    reduction_file = os.path.join(reduction_path, constants.REDUCTION_FILENAME)

    try:
        response['metadata'] = json.loads(storage.get_file(metadata_file))
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction folder or metadata file doesn't exist"}
        )

    try:
        response['labels'] = json.loads(storage.get_file(labels_file))
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction folder or labels file doesn't exist"}
        )

    try:
        response['reduction'] = json.loads(storage.get_file(reduction_file))
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Reduction folder or reduction file doesn't exist"}
        )


    return response


@router.post(
    "/experiments/{experiment_id}/reductions",
    tags=["reduction"],
    summary="Submit new reduction task",
    response_model=MetadataTaskModel,
    status_code=201
)
def send_reduction_task_to_celery(
    reduction: Union[PCAModel, TSNEModel, UMAPModel],
    experiment_id: str, request: Request, user_id: dict = Depends(authorization)
):
    
    response = {}

    task = tasks.reduction.delay(
        reduction.algorithm, reduction.components, reduction.params.dict(), user_id, experiment_id)

    response['task_id'] = task.id

    return response

@router.delete(
    "/experiments/{experiment_id}/reductions/{reduction_id}",
    tags=["reduction"],
    summary="Delete reduction result",
    responses={
        200:{
            "description": "Reduction deleted",
        },
        404: {
            "description": "Item not found",
            "model": ErrorModel
        }
    }
)
def delete_single_reduction(experiment_id: str, reduction_id: str, request: Request, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    reduction_path = os.path.join(data_dir, experiment_id, constants.REDUCTION_DIR, reduction_id)

    try:
        storage.delete(reduction_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Probably the reduction-id is not valid. But may be also that experiment-id is not valid or user-id is not valid"}
        )

    return True
