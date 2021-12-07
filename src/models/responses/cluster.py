from typing import List
from pydantic import BaseModel


###############################################################################
# Submodels
###############################################################################


class Metadata(BaseModel):
    algorithm: str
    params: dict
    start_datetime: str
    end_datetime: str
    seconds_elapsed: int


###############################################################################
# Models
###############################################################################


class ClusterBaseModel(BaseModel):
    id: str
    metadata: Metadata


class ClusterModel(BaseModel):
    metadata: Metadata
    cluster: List[int]
