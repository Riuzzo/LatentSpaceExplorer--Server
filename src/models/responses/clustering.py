from typing import List
from pydantic import BaseModel
from typing import Optional


# params

class MetadataParams(BaseModel):
    algorithm: str
    params: dict
    start_datetime: str
    end_datetime: str
    seconds_elapsed: int


# models

class MetadataClusteringModel(BaseModel):
    id: str
    metadata: MetadataParams


class ClusteringModel(BaseModel):
    metadata: MetadataParams
    cluster: List[int]
