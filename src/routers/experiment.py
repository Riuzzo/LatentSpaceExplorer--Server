import os
import json
import owncloud

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List

from src.models.responses.experiment import MetadataExperimentModel, ExperimentModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

router = APIRouter()

@router.get(
    "/experiments",
    tags=["experiment"],
    summary="Get experiments",
    response_model=List[MetadataExperimentModel],
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

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    try:
        experiments = storage.list(data_dir, depth=1)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "User folder doesn't exist"}
        )

    for exp in experiments:
        if exp.file_type != 'file':
            experiment = {}
        
            metadata_path = os.path.join(exp.path, constants.METADATA_FILENAME)

            experiment["id"] = exp.name
        
            try:
                metadata = storage.get_file(metadata_path)
                experiment['metadata'] = json.loads(metadata)
                response.append(experiment)    
        
            except owncloud.owncloud.HTTPResponseError:
                pass # If the file is deleted, don't add it to the list

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

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    experiment_path = os.path.join(data_dir, experiment_id)

    metadata_path = os.path.join(experiment_path, 'metadata.json')
    
    try:
        metadata = storage.get_file(metadata_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment-id not valid"}
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

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    experiment_path = os.path.join(data_dir, experiment_id)

    try:
        storage.delete(experiment_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment-id not valid or user folder doesn't exist"}
        )

    return True
