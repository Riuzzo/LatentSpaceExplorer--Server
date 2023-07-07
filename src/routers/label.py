import os
import json
import time

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from models.responses.label import LabelModel
from models.responses.error import ErrorModel

import utils.constants as constants
from utils.authorization import authorization


import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/labels",
    tags=["label"],
    summary="Get labels",
    response_model=LabelModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_labels(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = {}
    storage = request.state.storage

    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
    else:
        user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
        experiment_dir = os.path.join(user_dir, experiment_id)
    
    labels_path = os.path.join(experiment_dir, constants.LABELS_FILENAME)

    try:
        labels = storage.get_file(labels_path)
        response = json.loads(labels)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='get_labels', subaction="get_file", status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.file_exist(labels_path):
            logger.error(message='Experiment labels file not exist', action='get_labels', subaction="get_file", status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Labels file not exist"}
            )
    elapsed = time.time() - total_time
    logger.info(message='Labels retrieved', duration=elapsed, action='get_labels', status='SUCCED', resource='lse-service', userid=user_id)
    return response
