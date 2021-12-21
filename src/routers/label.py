import os
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.models.responses.label import LabelModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization


router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/labels",
    tags=["label"],
    summary="Get labels",
    response_model=LabelModel,
    responses={
        404: {
            "description": "Label not found",
            "model": ErrorModel
        }
    }
)
def get_labels(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    labels_path = os.path.join(experiment_dir, constants.LABELS_FILENAME)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.file_exist(labels_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Labels file not exist"}
        )

    labels = storage.get_file(labels_path)
    response = json.loads(labels)

    return response
