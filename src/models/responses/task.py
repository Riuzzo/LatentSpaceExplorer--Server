from pydantic import BaseModel
from typing import Optional


###############################################################################
# Models
###############################################################################


class TaskBaseModel(BaseModel):
    task_id: str


class TaskModel(BaseModel):
    task_id: str
    status: str
    name: Optional[str]
    result_id: Optional[str]
