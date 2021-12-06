from pydantic import BaseModel
from typing import Dict, List


###############################################################################
# Submodels
###############################################################################


class PreviewModel(BaseModel):
    r: int
    g: int
    b: int


class ChannelsModel(BaseModel):
    map: Dict
    preview: PreviewModel


class ImageModel(BaseModel):
    format: str
    dim: int
    channels: ChannelsModel


class DatasetModel(BaseModel):
    split_threshold: int


class PreprocessingModel(BaseModel):
    normalization_type: str


class AugmentationModel(BaseModel):
    threshold: int
    flip_x: bool
    flip_y: bool
    rotate: Dict
    shift: Dict


class ArchitectureModel(BaseModel):
    name: str
    filters: List
    latent_dim: int


class TrainingModel(BaseModel):
    epochs: int
    batch_size: int
    optimizer: Dict
    loss: str


class MetadataModel(BaseModel):
    name: str
    image: ImageModel
    dataset: DatasetModel
    preprocessing: PreprocessingModel
    augmentation: AugmentationModel
    architecture: ArchitectureModel
    training: TrainingModel


###############################################################################
# Models
###############################################################################


class ExperimentBaseModel(BaseModel):
    metadata: MetadataModel


class ExperimentModel(BaseModel):
    id: str
    metadata: MetadataModel
