from pydantic import BaseModel
from typing import List


# params

class Preview(BaseModel):
    r: int
    g: int
    b: int

class Image(BaseModel):
    dim: int
    channels: int
    preview: Preview

class Dataset(BaseModel):
    split_threshold: int
    augmentation_threshold: int

class Architecture(BaseModel):
    name: str
    filters: List
    latent_dim: int

class Training(BaseModel):
    epochs: int
    batch_size: int
    optimizer: str
    lr: float
    loss: str

class MetadataParams(BaseModel):
    name: str
    image: Image
    dataset: Dataset
    architecture: Architecture
    training: Training

# models

class MetadataExperimentModel(BaseModel):
    id: str
    metadata: MetadataParams


class ExperimentModel(BaseModel):
    metadata: MetadataParams
