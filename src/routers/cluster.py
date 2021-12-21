import os
import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from typing import Union, List

from src.celery_app import tasks
from src.models.requests.cluster import DBSCANModel, AffinityPropagationModel, KMeansModel, AgglomerativeClusteringModel, SpectralClusteringModel, OPTICSModel, GaussianMixtureModel, BirchModel
from src.models.responses.cluster import ClusterBaseModel, ClusterModel, ClusterPendingModel
from src.models.responses.task import TaskBaseModel
from src.models.responses.error import ErrorModel

import src.utils.constants as constants
from src.utils.authorization import authorization


router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/clusters",
    tags=["cluster"],
    summary="Get clusters",
    response_model=List[ClusterBaseModel],
    responses={
        404: {
            "description": "Cluster not found",
            "model": ErrorModel
        }
    }
)
def get_clusters(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    clusters_dir = os.path.join(experiment_dir, constants.CLUSTER_DIR)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.dir_exist(clusters_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Clusters dir not valid"}
        )

    clusters = storage.list(clusters_dir)

    for cluster in clusters:
        if cluster.file_type == 'dir':
            clus = {}
            clus["id"] = cluster.name

            metadata_path = os.path.join(
                cluster.path, constants.METADATA_FILENAME)

            if storage.file_exist(metadata_path):
                metadata = storage.get_file(metadata_path)
                clus['metadata'] = json.loads(metadata)
                response.append(clus)

    return response


@router.get(
    "/experiments/{experiment_id}/clusters/pending",
    tags=["cluster"],
    summary="Get pending clusters count",
    response_model=ClusterPendingModel,
)
def get_pending_clusters_count(experiment_id: str, user_id: dict = Depends(authorization)):
    response = {}
    response['count'] = 0

    inspector = tasks.celery.control.inspect()
    celery_servers = inspector.active().keys()

    for server_id in celery_servers:
        server = inspector.active().get(server_id)

        for task in server:
            if 'cluster' == task['name'] and \
                    experiment_id == task['kwargs']['experiment_id'] and \
                    user_id == task['kwargs']['user_id']:

                response['count'] += 1

    return response


@router.get(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Get cluster",
    response_model=ClusterModel,
    responses={
        404: {
            "description": "Cluster not found",
            "model": ErrorModel
        }
    }
)
def get_cluster(request: Request, experiment_id: str, cluster_id: str, user_id: dict = Depends(authorization)):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    cluster_dir = os.path.join(
        experiment_dir, constants.CLUSTER_DIR, cluster_id)
    metadata_path = os.path.join(cluster_dir, constants.METADATA_FILENAME)
    cluster_path = os.path.join(cluster_dir, constants.CLUSTER_FILENAME)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    if not storage.dir_exist(cluster_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Cluster id not valid"}
        )

    if not storage.file_exist(metadata_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Cluster metadata file not exist"}
        )

    if not storage.file_exist(cluster_path):
        return JSONResponse(
            status_code=404,
            content={"message": "Cluster file not exist"}
        )

    metadata = storage.get_file(metadata_path)
    response['metadata'] = json.loads(metadata)

    cluster = storage.get_file(cluster_path)
    response['groups'] = json.loads(cluster)

    return response


@router.post(
    "/experiments/{experiment_id}/clusters",
    tags=["cluster"],
    summary="Create new cluster",
    response_model=TaskBaseModel,
    status_code=201
)
def post_cluster(
    request: Request,
    cluster: Union[
        AffinityPropagationModel, DBSCANModel, KMeansModel, AgglomerativeClusteringModel, SpectralClusteringModel, OPTICSModel, GaussianMixtureModel, BirchModel
    ],
    experiment_id: str, user_id: dict = Depends(authorization)
):
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={"message": "Experiment id not valid"}
        )

    task = tasks.cluster.apply_async(
        kwargs={
            "algorithm": cluster.algorithm,
            "params": cluster.params.dict(),
            "experiment_id": experiment_id,
            "user_id": user_id
        }
    )

    response['task_id'] = task.id

    return response


@router.delete(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Delete cluster",
    responses={
        200: {
            "description": "Cluster deleted",
        },
        404: {
            "description": "Cluster not found",
            "model": ErrorModel
        }
    }
)
def delete_cluster(request: Request, experiment_id: str, cluster_id: str, user_id: dict = Depends(authorization)):
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    experiment_dir = os.path.join(user_dir, experiment_id)
    cluster_dir = os.path.join(
        experiment_dir, constants.CLUSTER_DIR, cluster_id)

    if not storage.dir_exist(experiment_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": "Experiment id not valid"}
        )

    if not storage.dir_exist(cluster_dir):
        return JSONResponse(
            status_code=404,
            content={
                "message": "Cluster id not valid"}
        )

    storage.delete(cluster_dir)

    return True
