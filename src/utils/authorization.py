from fastapi import Header, Request, HTTPException
from pydantic import Required

import src.utils.constants as constants


def authorization(request: Request, user_id: str = Header(Required)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    if not storage.dir_exist(user_dir):
        raise HTTPException(
            status_code=404,
            detail="User directory doesn't exist. Make sure you have uploaded it to NextCloud and shared it with the service user."
        )

    return user_id
