from pydantic import BaseModel


###############################################################################
# Models
###############################################################################


class StatusModel(BaseModel):
    server: bool
    queue: bool
    scheduler: bool
