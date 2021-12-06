import owncloud

from fastapi import Header, Request, HTTPException
from pydantic import Required

import src.utils.constants as constants


def authorization(request: Request, user_id: str = Header(Required)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    try:
        dir = storage.file_info(user_dir)

        if dir.file_type != 'dir':
            raise HTTPException(
                status_code=404,
                detail="User directory doesn't exist. Make sure you have uploaded it to NextCloud and shared it with the service user."
            )

    except owncloud.owncloud.HTTPResponseError:
        raise HTTPException(
            status_code=404,
            detail="Error on looking for the user's directory."
        )

    return user_id
