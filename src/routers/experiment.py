import os
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List

from src.models.responses.experiment import ExperimentBaseModel, ExperimentModel, ExperimentPublicImagesFolderNameModel
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
    experiments = storage.list(user_dir, depth=2)

    for experiment in experiments:
        file_type = experiment.file_type
        file_name = os.path.basename(experiment.path)

        if file_type == 'file' and file_name == constants.METADATA_FILENAME:
            exp = {}

            exp["id"] = experiment.path.split(os.path.sep)[2]

            metadata = storage.get_file(experiment.path)
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
    metadata_path = os.path.join(experiment_dir, constants.METADATA_FILENAME)

    try:
        metadata = storage.get_file(metadata_path)
        response['metadata'] = json.loads(metadata)

    except:
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

    try:
        storage.delete(experiment_dir)

    except:
        if not storage.dir_exist(experiment_dir):
            return JSONResponse(
                status_code=404,
                content={
                    "message": "Experiment id not valid"}
            )

    return True


@router.get(
    "/experiments/{experiment_id}/public-images-folder-name",
    tags=["experiment"],
    summary="Get experiment public images folder name",
    response_model=ExperimentPublicImagesFolderNameModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_experiment_public_images_folder_name(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    images_dir = os.path.join(data_dir, experiment_id, constants.IMAGES_DIR)

    try:
        public_name = storage.get_link(images_dir)
        response['images_folder_name'] = os.path.split(public_name)[-1]

    except:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment images public folder name not exist"}
        )

    return response
