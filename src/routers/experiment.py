import os
import json
import owncloud

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List

from src.models.responses.experiment import ExperimentsModel, ExperimentModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

router = APIRouter()


@router.get(
    "/experiments",
    tags=["experiment"],
    summary="Get experiments",
    response_model=List[ExperimentsModel],
    responses={
        404: {
            "description": "Item not found",
            "model": ErrorModel
        }
    }
)
def get_experiments(request: Request, user_id: dict = Depends(authorization)):
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiments = storage.list(user_dir, depth=1)

    for experiment in experiments:
        if experiment.file_type == 'dir':
            exp = {}

            metadata_path = os.path.join(
                experiment.path, constants.METADATA_FILENAME)

            exp["id"] = experiment.name

            try:
                metadata = storage.get_file(metadata_path)
                exp['metadata'] = json.loads(metadata)
                response.append(exp)

            except owncloud.owncloud.HTTPResponseError:
                pass

    return response


@router.get(
    "/experiments/{experiment_id}",
    tags=["experiment"],
    summary="Get experiment",
    response_model=ExperimentModel,
    responses={
        404: {
            "description": "Item not found",
            "model": ErrorModel
        }
    }
)
def get_experiment(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_path = os.path.join(user_dir, experiment_id)
    metadata_path = os.path.join(experiment_path, 'metadata.json')

    try:
        metadata = storage.get_file(metadata_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    response['metadata'] = json.loads(metadata)

    return response


@router.delete(
    "/experiments/{experiment_id}",
    tags=["experiment"],
    summary="Delete experiment",
    responses={
        404: {
            "description": "Item not found",
            "model": ErrorModel
        }
    }
)
def delete_experiment(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_path = os.path.join(user_dir, experiment_id)

    try:
        storage.delete(experiment_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={
                "message": "Experiment id not valid"}
        )

    return True
