import os
import json
import time

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import List

from src.models.responses.experiment import ExperimentBaseModel, ExperimentModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()

#initial_time = time.time()
#elapsed = time.time() - initial_time
#logger.info(message='Listed experiments', duration=elapsed, action='get_experiments', subaction='list_experiments', status='SUCCED', resource='lse-service', userid=user_id)

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
    total_time = time.time()
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    initial_time = time.time()
    experiments = storage.list(user_dir, depth=2)
    elapsed = time.time() - initial_time
    logger.debug(message='Retrieved user\'s folder tree', duration=elapsed, action='get_experiments', subaction='list_experiments', status='SUCCED', resource='lse-service', userid=user_id)
    for experiment in experiments:
        file_type = experiment.file_type
        file_name = os.path.basename(experiment.path)

        if file_type == 'file' and file_name == constants.METADATA_FILENAME:
            exp = {}

            exp["id"] = experiment.path.split(os.path.sep)[2]
            initial_time = time.time()
            metadata = storage.get_file(experiment.path)
            elapsed = time.time() - initial_time
            logger.debug(message='Metadata retrieved', duration=elapsed, action='get_experiments', subaction='get_medata', status='SUCCED', resource='lse-service', userid=user_id)
            exp['metadata'] = json.loads(metadata)

            response.append(exp)
    elapsed = time.time() - total_time
    logger.info(message='get_experiments', duration=elapsed, action='get_experiments', status='SUCCED', resource='lse-service', userid=user_id)
    return response

# Function unused
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
        initial_time = time.time()
        metadata = storage.get_file(metadata_path)
        elapsed = time.time() - initial_time
        logger.info(message='Metadata retrieved', duration=elapsed, action='get_experiment', subaction='get_metadata', status='SUCCED', resource='lse-service', userid=user_id)
        response['metadata'] = json.loads(metadata)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', duration=elapsed, action='get_experiment', subaction='get_metadata', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.file_exist(metadata_path):
            logger.error(message='Experiment metadata file not exist', duration=elapsed, action='get_experiment', subaction='get_metadata', status='FAILED', resource='lse-service', userid=user_id)
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
        logger.info(message='{} experiment deleted'.format(experiment_dir), action='delete_experiment', status='SUCCED', resource='lse-service', userid=user_id)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id {} not valid'.format(experiment_dir), action='delete_experiment', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={
                    "message": "Experiment id not valid"}
            )

    return True
