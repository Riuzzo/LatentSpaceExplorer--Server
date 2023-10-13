import os
import json
import time

from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List

from models.responses.experiment import ExperimentBaseModel, ExperimentModel
from models.responses.error import ErrorModel

import utils.constants as constants
from utils.authorization import authorization
from utils.storage import Storage

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()

def check_and_create_user_demo_folder(user_id: str, storage: Storage, experiment_id: str):
    user_dir = '{}{}'.format("data-", user_id)
    user_demo_path = os.path.join(constants.DEMO_DIR, experiment_id, user_dir)
    
    if not(storage.dir_exist(user_demo_path)):
        storage.mkdir(user_demo_path)
    
    user_reduction_path = os.path.join(user_demo_path, constants.REDUCTION_DIR)
    if not(storage.dir_exist(user_reduction_path)):
        demo_reduction_path = os.path.join(constants.DEMO_DIR, experiment_id, constants.REDUCTION_DIR)
        storage.copy(demo_reduction_path, user_reduction_path)

    user_cluster_path = os.path.join(user_demo_path, constants.CLUSTER_DIR)
    if not(storage.dir_exist(user_cluster_path)):
        demo_cluster_path = os.path.join(constants.DEMO_DIR, experiment_id, constants.CLUSTER_DIR)
        storage.copy(demo_cluster_path, user_cluster_path)


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
def get_experiments(request: Request, background_tasks: BackgroundTasks, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = []
    storage = request.state.storage

    # Demo experiments
    experiments = storage.list(constants.DEMO_DIR, depth=2)
    for experiment in experiments:
        file_type = experiment.file_type
        file_name = os.path.basename(experiment.path)

        if file_type == 'file' and file_name == constants.METADATA_FILENAME:
            exp = {}

            exp["id"] = experiment.path.split(os.path.sep)[2]
            print(experiment.path)
            metadata = storage.get_file(experiment.path)
            exp['metadata'] = json.loads(metadata)

            response.append(exp)
            background_tasks.add_task(check_and_create_user_demo_folder, user_id=user_id, storage=storage, experiment_id=exp["id"])

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

    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
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
    else:
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
    if experiment_id.startswith("demo"):
        return JSONResponse(
                status_code=200, # to make it 403 when client it's fixed
                content={
                    "message": "Demo project cannot be deleted"}
            )
    
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
