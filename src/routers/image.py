import time
import os
import owncloud

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl

from src.models.responses.image import ImagesFolderModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/images/folder-name",
    tags=["image"],
    summary="Get public images folder name",
    response_model=ImagesFolderModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_images_folder_name(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = {}
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    images_dir = os.path.join(data_dir, experiment_id, constants.IMAGES_DIR)

    try:
        public_name = storage.get_link(images_dir)
        response['images_folder_name'] = os.path.split(public_name)[-1]

    except:
        logger.error(message='Experiment images folder name not exist', action='get_images_folder_name', status='FAILED', resource='lse-service', userid=user_id)
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment images folder name not exist"}
        )
    elapsed = time.time() - total_time
    logger.info(message='Folder link retrieved', duration=elapsed, action='get_images_folder_name', status='SUCCED', resource='lse-service', userid=user_id)
    return response


@router.get(
    "/experiments/{experiment_id}/images/{image_name}",
    tags=["image"],
    summary="Get single image",
    response_model=AnyHttpUrl,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_single_image(request: Request, image_name: str, experiment_id: str, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    image_path = os.path.join(data_dir, experiment_id,
                              constants.IMAGES_DIR, image_name)

    try:
        link = storage.get_link(image_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "The image doesn't exist"}
        )

    return '{}{}'.format(link, "/preview")
