from typing import List
from pydantic import BaseModel


# params

class MetadataParams(BaseModel):
    embeddings_file: str
    algorithm: str
    components: int
    params: dict
    reduction_file: str
    start_datetime: str
    end_datetime: str
    seconds_elapsed: int


# models

class MetadataReductionModel(BaseModel):
    id: str
    metadata: MetadataParams


class ReductionModel(BaseModel):
    metadata: MetadataParams
    reduction: List[List[float]]
    labels: List[str]
