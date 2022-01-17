import os
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List

from src.models.responses.experiment import ExperimentBaseModel, ExperimentModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

router = APIRouter()


@router.get(
    "/experiments",
    tags=["experiment"],
    summary="Get experiments",
    response_model=List[ExperimentModel],
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_experiments(request: Request, user_id: dict = Depends(authorization)):
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiments = storage.list(user_dir)

    for experiment in experiments:
        if experiment.file_type == 'dir':
            exp = {}
            exp["id"] = experiment.name

            metadata_path = os.path.join(
                experiment.path, constants.METADATA_FILENAME)

            if storage.file_exist(metadata_path):
                metadata = storage.get_file(metadata_path)
                exp['metadata'] = json.loads(metadata)
                response.append(exp)

    return response


@router.get(
    "/experiments/{experiment_id}",
    tags=["experiment"],
    summary="Get experiment",
    response_model=ExperimentBaseModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_experiment(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    metadata_path = os.path.join(experiment_dir, 'metadata.json')

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.file_exist(metadata_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment metadata file not exist"}
        )

    metadata = storage.get_file(metadata_path)
    response['metadata'] = json.loads(metadata)

    return response


@router.delete(
    "/experiments/{experiment_id}",
    tags=["experiment"],
    summary="Delete experiment",
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def delete_experiment(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": "Experiment id not valid"}
        )

    storage.delete(experiment_dir)

    return True
