from fastapi import Header
from pydantic import Required


def authorization(user_id: str = Header(Required)):

    # TODO: check if user dir exist

    return user_id
