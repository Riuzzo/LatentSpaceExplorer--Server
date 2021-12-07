from pydantic import BaseModel, Field
from typing import Literal


###############################################################################
# Submodels
###############################################################################

class AffinityPropagation(BaseModel):
    pass


class DBSCAN(BaseModel):
    eps: float = Field(ge=0.1, le=1)
    min_samples: int = Field(ge=1, le=300)


class KMeans(BaseModel):
    n_clusters: int = Field(ge=1, le=100)


class AgglomerativeClustering(BaseModel):
    distance_threshold: int = Field(ge=1, le=100)


###############################################################################
# Models
###############################################################################


class AffinityPropagationModel(BaseModel):
    algorithm: Literal['affinity_propagation']
    params: AffinityPropagation


class DBSCANModel(BaseModel):
    algorithm: Literal['dbscan']
    params: DBSCAN


class KMeansModel(BaseModel):
    algorithm: Literal['kmeans']
    params: KMeans


class AgglomerativeClusteringModel(BaseModel):
    algorithm: Literal['agglomerative_clustering']
    params: AgglomerativeClustering
