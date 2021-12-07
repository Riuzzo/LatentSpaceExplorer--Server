from pydantic import BaseModel, Field
from typing import Literal


###############################################################################
# Submodels
###############################################################################


class DBSCAN(BaseModel):
    eps: float = Field(ge=0.1, le=1)
    min_samples: int = Field(ge=1, le=300)


class AffinityPropagation(BaseModel):
    pass


class KMeans(BaseModel):
    n_clusters: int = Field(ge=1, le=100)


class AgglomerativeClustering(BaseModel):
    distance_threshold: int = Field(ge=1, le=100)


class SpectralClustering(BaseModel):
    n_clusters: int = Field(ge=1, le=100)


class OPTICS(BaseModel):
    n_clusters: int = Field(ge=1, le=100)
    min_samples: int = Field(ge=1, le=300)


###############################################################################
# Models
###############################################################################


class DBSCANModel(BaseModel):
    algorithm: Literal['dbscan']
    params: DBSCAN


class AffinityPropagationModel(BaseModel):
    algorithm: Literal['affinity_propagation']
    params: AffinityPropagation


class KMeansModel(BaseModel):
    algorithm: Literal['kmeans']
    params: KMeans


class AgglomerativeClusteringModel(BaseModel):
    algorithm: Literal['agglomerative_clustering']
    params: AgglomerativeClustering


class SpectralClusteringModel(BaseModel):
    algorithm: Literal['spectral_clustering']
    params: SpectralClustering


class OPTICSModel(BaseModel):
    algorithm: Literal['optics']
    params: OPTICS
