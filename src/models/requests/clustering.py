from pydantic import BaseModel, Field
from typing import Literal


##########################################
############### PARAMS ###################
##########################################

class AffinityPropagationParams(BaseModel):
    pass


class DBSCANParams(BaseModel):
    eps: float = Field(ge=0.1, le=1)
    min_samples: int = Field(ge=1, le=300)


class KMeansParams(BaseModel):
    n_clusters: int = Field(ge=1, le=100)


class AgglomerativeClusteringParams(BaseModel):
    distance_threshold: int = Field(ge=1, le=100)


##########################################
############### MODELS ###################
##########################################

class AffinityPropagationModel(BaseModel):
    algorithm: Literal['affinity_propagation']
    params: AffinityPropagationParams


class DBSCANModel(BaseModel):
    algorithm: Literal['dbscan']
    params: DBSCANParams


class KMeansModel(BaseModel):
    algorithm: Literal['kmeans']
    params: KMeansParams


class AgglomerativeClusteringModel(BaseModel):
    algorithm: Literal['agglomerative_clustering']
    params: AgglomerativeClusteringParams
