import os
import json
import time

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

import structlog

logger = structlog.getLogger("json_logger")

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
    total_time = time.time()
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
        initial_time = time.time()
        reductions = storage.list(reductions_dir, depth=2)
        elapsed = time.time() - initial_time
        logger.debug(message='Listing reductions', action='get_reductions', subaction="list", status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='get_reductions', subaction="list", status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.dir_exist(reductions_dir):
            logger.error(message='Reductions dir not valid', action='get_reductions', subaction="list", status='FAILED', resource='lse-service', userid=user_id)
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

            initial_time = time.time()
            metadata = storage.get_file(reduction.path)
            elapsed = time.time() - initial_time
            logger.debug(message='Getting metadata', action='get_reductions', subaction="get_file", status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
            red['metadata'] = json.loads(metadata)

            response.append(red)

    elapsed = time.time() - total_time
    logger.info(message='Get reductions', action='get_reductions', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
    return response


@router.get(
    "/experiments/{experiment_id}/reductions/pending",
    tags=["reduction"],
    summary="Get pending reductions count",
    response_model=ReductionPendingModel,
)
def get_pending_reductions_count(experiment_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    
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
    
    elapsed = time.time() - total_time
    logger.info(message='{} reductions in pending'.format(response['count']), action='get_pending_reductions_count', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
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
    total_time = time.time()
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
    try:
        # TODO make it more efficient, less call and split labels file to be less heavy to be readed
        initial_time = time.time()
        metadata = storage.get_file(metadata_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Getting metadata', action='get_reduction', subaction="get_metadata_file", status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
        response['metadata'] = json.loads(metadata)

        initial_time = time.time()
        reduction = storage.get_file(reduction_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Getting reduction', action='get_reduction', subaction="get_reduction_file", status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
        response['points'] = json.loads(reduction)

        initial_time = time.time()
        labels = storage.get_file(labels_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Getting labels', action='get_reduction', subaction="get_labels_file", status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
        labels = json.loads(labels)
        response['ids'] = labels['columns']

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='get_reduction', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.dir_exist(reduction_dir):
            logger.error(message='Reduction id not valid', action='get_reduction', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction id not valid"}
            )

        if not storage.file_exist(metadata_path):
            logger.error(message='Metadata file not valid', action='get_reduction', subaction='get_metadata_file', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction metadata file not exist"}
            )

        if not storage.file_exist(reduction_path):
            logger.error(message='Reduction file not valid', action='get_reduction', subcation='get_reduction_file', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction file not exist"}
            )

        if not storage.file_exist(labels_path):
            logger.error(message='Labels file not valid', action='get_reduction', subaction='get_labels_file', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction label file not exist"}
            )
    
    elapsed = time.time() - total_time
    logger.info(message='Get reduction', action='get_reduction', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
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
    total_time = time.time()
    response = {}
    storage = request.state.storage


    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        user_reductions_dir = 'data-{}'.format(user_id)
        reductions_dir = os.path.join(experiment_dir, user_reductions_dir, constants.CLUSTER_DIR)
    else:
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
    elapsed = time.time() - total_time
    logger.info(message='Calculate reduction task added', action='post_reduction', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
    logger.accounting(message='Posted reduction task', action='Reduction', value=1, measure="unit", resource='lse', userid=user_id)
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
    total_time = time.time()
    storage = request.state.storage

    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        user_reduction_dir = 'data-{}'.format(user_id)
        reduction_dir = os.path.join(experiment_dir, user_reduction_dir, constants.CLUSTER_DIR, reduction_id)
    else:
        user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
        experiment_dir = os.path.join(user_dir, experiment_id)
        reduction_dir = os.path.join(
            experiment_dir, constants.REDUCTION_DIR, reduction_id)

    try:
        initial_time = time.time()
        storage.delete(reduction_dir)
        elapsed = time.time() - initial_time
        logger.debug(message='Reduction deleted', action='delete_reduction', subaction='delete_reduction_dir', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='delete_reduction', subaction='delete_reduction_dir', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.dir_exist(reduction_dir):
            logger.error(message='Reduction id not valid', action='delete_reduction', subaction='delete_reduction_dir', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Reduction id not valid"}
            )

    elapsed = time.time() - total_time
    logger.info(message='Delete reduction', action='delete_reduction', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)

    return True
