import time
from fastapi import Header, Request
from pydantic import Required

import src.utils.constants as constants


class AuthError(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id


def authorization(request: Request, user_id: str = Header(Required)):
    attempts = 3

    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    user_dir_exist = storage.dir_exist(user_dir)

    while not user_dir_exist and attempts > 0:
        user_dir_exist = storage.dir_exist(user_dir)
        attempts -= 1
        time.sleep(3)

    if not user_dir_exist:
        raise AuthError(user_id=user_dir)

    return user_id
