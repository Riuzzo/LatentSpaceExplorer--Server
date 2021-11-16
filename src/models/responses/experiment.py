from pydantic import BaseModel
from typing import Dict, List


# params

class Preview(BaseModel):
    r: int
    g: int
    b: int

class Channels(BaseModel):
    map: Dict
    preview: Preview

class Image(BaseModel):
    format: str
    dim: int
    channels: Channels

class Dataset(BaseModel):
    split_threshold: int

class Preprocessing(BaseModel):
    normalization_type: str

class Augmentation(BaseModel):
    threshold: int
    flip_x: bool
    flip_y: bool
    rotate: Dict
    shift: Dict

class Architecture(BaseModel):
    name: str
    filters: List
    latent_dim: int

class Training(BaseModel):
    epochs: int
    batch_size: int
    optimizer: Dict
    loss: str

class MetadataParams(BaseModel):
    name: str
    image: Image
    dataset: Dataset
    preprocessing: Preprocessing
    augmentation: Augmentation
    architecture: Architecture
    training: Training

# models

class MetadataExperimentModel(BaseModel):
    id: str
    metadata: MetadataParams


class ExperimentModel(BaseModel):
    metadata: MetadataParams
