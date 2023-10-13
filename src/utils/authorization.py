import time
from fastapi import Header, Request
from pydantic import Required

import utils.constants as constants

import structlog

logger = structlog.getLogger("json_logger")

class AuthError(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id


def authorization(request: Request, user_id: str = Header(Required)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    initial_time = time.time()
    user_dir_exist = storage.dir_exist(user_dir)
    elapsed = time.time() - initial_time
    if not user_dir_exist:
        logger.error(message='User dir doesn\'t exist', duration=elapsed, action='authorization', subaction="check_folder_exist", status='FAILED', resource='lse-service', userid=user_id)
        raise AuthError(user_id=user_dir)

    logger.debug(message='User dir exist', duration=elapsed, action='authorization', subaction="check_folder_exist", status='SUCCED', resource='lse-service', userid=user_id)
    return user_id
