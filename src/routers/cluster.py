import os
import owncloud

from fastapi import APIRouter, Header, Request, Depends
from fastapi.responses import JSONResponse
from typing import Union, List

from src.celery_app import tasks
from src.models.requests.clustering import AffinityPropagationModel, DBSCANModel, KMeansModel, AgglomerativeClusteringModel
from src.models.responses.clustering import MetadataClusteringModel, ClusteringModel
from src.models.responses.task import MetadataTaskModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization

import json

router = APIRouter()

@router.get(
    "/experiments/{experiment_id}/clusters",
    tags=["cluster"],
    summary="Get all cluster's metadata",
    response_model=List[MetadataClusteringModel]
)
def get_all_clusters(experiment_id: str, request: Request, user_id: dict = Depends(authorization)):
    response = []

    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    path = os.path.join(data_dir, experiment_id, constants.CLUSTER_DIR)
    
    try:
        clusters = storage.list(path, depth=1)
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment doesn't exist"}
        )

    for clus in clusters:
        if clus.file_type == 'dir':
            record = {}
            record["id"] = clus.name
            path = os.path.join(clus.path, constants.METADATA_FILENAME)
            try:
                record['metadata'] = json.loads(storage.get_file(path))
                response.append(record)
            except owncloud.owncloud.HTTPResponseError:
                pass # If the file is deleted, don't add it to the list
    
    return response


@router.get(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Get single cluster result",
    response_model=ClusteringModel,
    responses={
        404: {
            "description": "Cluster not found",
            "model": ErrorModel
        }
    }
)
def get_single_cluster(cluster_id: str, experiment_id: str, request: Request, user_id: dict = Depends(authorization)):
    response = {}
    
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    experiment_path = os.path.join(data_dir, experiment_id)
    cluster_path = os.path.join(experiment_path, constants.CLUSTER_DIR, cluster_id)

    metadata_file = os.path.join(cluster_path, constants.METADATA_FILENAME)
    cluster_file = os.path.join(cluster_path, constants.CLUSTER_FILENAME)
    
    try:
        response['metadata'] = json.loads(storage.get_file(metadata_file))
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Cluster folder or metadata file doesn't exist"}
        )

    try:
        response['cluster'] = json.loads(storage.get_file(cluster_file))
    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Cluster folder or cluster file doesn't exist"}
        )
    response['cluster'] = json.loads(storage.get_file(cluster_file))

    return response

@router.post(
    "/experiments/{experiment_id}/clusters",
    tags=["cluster"],
    summary="Submit new clustering task",
    response_model=MetadataTaskModel,
    status_code=201
)
def send_clustering_task_to_celery(
    clustering: Union[AffinityPropagationModel, DBSCANModel,
                      KMeansModel, AgglomerativeClusteringModel], experiment_id: str, request: Request, user_id: dict = Depends(authorization) 
):
    response = {}

    task = tasks.clustering.delay(
        clustering.algorithm, clustering.params.dict(), user_id, experiment_id)

    response['task_id'] = task.id

    return response

@router.delete(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Delete cluster result",
    responses={
        200:{
            "description": "Cluster deleted",
        },
        404: {
            "description": "Item not found",
            "model": ErrorModel
        }
    }
)
def delete_single_cluster(experiment_id: str, cluster_id: str, request: Request, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    data_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    
    cluster_path = os.path.join(data_dir, experiment_id, constants.CLUSTER_DIR, cluster_id)

    try:
        storage.delete(cluster_path)

    except owncloud.owncloud.HTTPResponseError:
        return JSONResponse(
            status_code=404,
            content={"message": "Probably the cluster-id is not valid. But may be also that experiment-id is not valid or user-id is not valid"}
        )

    return True
