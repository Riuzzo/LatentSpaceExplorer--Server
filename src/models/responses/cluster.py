from typing import List, Union
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


class Scores(BaseModel):
    calinski_harabasz_score: float
    davies_bouldin_score: float


###############################################################################
# Models
###############################################################################


class ClusterBaseModel(BaseModel):
    id: str
    metadata: Metadata


class ClusterModel(BaseModel):
    metadata: Metadata
    groups: List[int]
    silhouettes: Union[List, List[float]]
    scores: Union[dict, Scores]


class ClusterPendingModel(BaseModel):
    count: int
