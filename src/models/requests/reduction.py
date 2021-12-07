from pydantic import BaseModel, Field
from typing import Literal


###############################################################################
# Submodels
###############################################################################


class PCA(BaseModel):
    pass


class TSNE(BaseModel):
    perplexity: int = Field(ge=5, le=50)
    iterations: int = Field(ge=250, le=5000)
    learning_rate: int = Field(ge=10, le=1000)


class UMAP(BaseModel):
    neighbors: int = Field(ge=2, le=200)
    min_distance: float = Field(ge=0.01, le=0.99)


###############################################################################
# Models
###############################################################################


class PCAModel(BaseModel):
    algorithm: Literal['pca']
    components: int = Field(ge=2, le=3)
    params: PCA


class TSNEModel(BaseModel):
    algorithm: Literal['tsne']
    components: int = Field(ge=2, le=3)
    params: TSNE


class UMAPModel(BaseModel):
    algorithm: Literal['umap']
    components: int = Field(ge=2, le=3)
    params: UMAP
