from pydantic import BaseModel, Field
from typing import Literal


###############################################################################
# Submodels
###############################################################################


class DBSCAN(BaseModel):
    eps: float = Field(ge=0.01, le=1)
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
    min_samples: int = Field(ge=1, le=300)
    metric: Literal['euclidean', 'cosine']


class GaussianMixture(BaseModel):
    n_components: int = Field(ge=1, le=100)


class Birch(BaseModel):
    n_clusters: int = Field(ge=1, le=100)


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


class GaussianMixtureModel(BaseModel):
    algorithm: Literal['gaussian_mixture']
    params: GaussianMixture


class BirchModel(BaseModel):
    algorithm: Literal['birch']
    params: Birch
