from fastapi import Header, Request
from pydantic import Required
from time import time

import src.utils.constants as constants


class AuthError(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id


def authorization(request: Request, user_id: str = Header(Required)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    start = time()
    user_dir_exist = storage.dir_exist(user_dir)
    elapsed = time() - start
    print("Authorization time")
    print(elapsed)

    if not user_dir_exist:
        raise AuthError(user_id=user_dir)

    return user_id
