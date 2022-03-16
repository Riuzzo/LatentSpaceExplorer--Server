import os
import json
import time

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

import structlog

logger = structlog.getLogger("json_logger")

router = APIRouter()


@router.get(
    "/experiments/{experiment_id}/clusters",
    tags=["cluster"],
    summary="Get clusters",
    response_model=List[ClusterBaseModel],
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_clusters(request: Request, experiment_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = []
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    experiment_dir = os.path.join(user_dir, experiment_id)
    clusters_dir = os.path.join(experiment_dir, constants.CLUSTER_DIR)

    clusters = []

    try:
        initial_time = time.time() 
        clusters = storage.list(clusters_dir, depth=2)
        elapsed = time.time() - initial_time
        logger.debug(message='Retrieved clusters', duration=elapsed, action='get_clusters', subaction='list_clusters', status='SUCCED', resource='lse-service', userid=user_id)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='get_clusters', subaction='list_clusters', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.dir_exist(clusters_dir):
            logger.error(message='Clusters dir not valid', action='get_clusters', subaction='list_clusters', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Clusters dir not valid"}
            )

    for cluster in clusters:
        file_type = cluster.file_type
        file_name = os.path.basename(cluster.path)

        if file_type == 'file' and file_name == constants.METADATA_FILENAME:
            clu = {}

            clu["id"] = cluster.path.split(os.path.sep)[4]
            initial_time = time.time()
            metadata = storage.get_file(cluster.path)
            elapsed = time.time() - initial_time
            logger.debug(message='Retrieved single cluster metadata', duration=elapsed, action='get_clusters', subaction='get_metadata', status='SUCCED', resource='lse-service', userid=user_id)
            clu['metadata'] = json.loads(metadata)

            response.append(clu)
    elapsed = time.time() - total_time
    logger.info(message='{} clusters retrieved'.format(len(response)    ), duration=elapsed, action='get_clusters', status='SUCCED', resource='lse-service', userid=user_id)
    return response


@router.get(
    "/experiments/{experiment_id}/clusters/pending",
    tags=["cluster"],
    summary="Get pending clusters count",
    response_model=ClusterPendingModel,
)
def get_pending_clusters_count(experiment_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = {}
    response['count'] = 0

    inspector = tasks.celery.control.inspect()
    workers = inspector.active().keys()

    for worker_id in workers:
        active = inspector.active().get(worker_id)
        reserved = inspector.reserved().get(worker_id)

        for task in active + reserved:
            if 'cluster' == task['name'] and \
                    experiment_id == task['kwargs']['experiment_id'] and \
                    user_id == task['kwargs']['user_id']:

                response['count'] += 1
    elapsed = time.time() - total_time
    logger.info(message='{} pending clusters retrieved'.format(response['count']), duration=elapsed, action='get_pending_clusters_count', status='SUCCED', resource='lse-service', userid=user_id)
    return response


@router.get(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Get cluster",
    response_model=ClusterModel,
    responses={
        404: {
            "model": ErrorModel
        }
    }
)
def get_cluster(request: Request, experiment_id: str, cluster_id: str, user_id: dict = Depends(authorization)):
    total_time = time.time()
    response = {}
    storage = request.state.storage

    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
    experiment_dir = os.path.join(user_dir, experiment_id)
    cluster_dir = os.path.join(experiment_dir, constants.CLUSTER_DIR, cluster_id)
    metadata_path = os.path.join(cluster_dir, constants.METADATA_FILENAME)
    cluster_path = os.path.join(cluster_dir, constants.CLUSTER_FILENAME)
    silhouette_path = os.path.join(cluster_dir, constants.SILHOUETTE_FILENAME)
    scores_path = os.path.join(cluster_dir, constants.SCORES_FILENAME)

    try:
        initial_time = time.time()
        metadata = storage.get_file(metadata_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Retrieved single cluster metadata', duration=elapsed, action='get_cluster', subaction='get_metadata', status='SUCCED', resource='lse-service', userid=user_id)
        response['metadata'] = json.loads(metadata)

        initial_time = time.time()
        cluster = storage.get_file(cluster_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Retrieved single cluster', duration=elapsed, action='get_cluster', subaction='get_cluster', status='SUCCED', resource='lse-service', userid=user_id)
        response['groups'] = json.loads(cluster)

        initial_time = time.time()
        silohuette = storage.get_file(silhouette_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Retrieved single cluster silhouette', duration=elapsed, action='get_cluster', subaction='get_silhouette', status='SUCCED', resource='lse-service', userid=user_id)
        response['silhouettes'] = json.loads(silohuette)

        initial_time = time.time()
        scores = storage.get_file(scores_path)
        elapsed = time.time() - initial_time
        logger.debug(message='Retrieved single cluster scores', duration=elapsed, action='get_cluster', subaction='get_scores', status='SUCCED', resource='lse-service', userid=user_id)
        response['scores'] = json.loads(scores)

    except:
        if not storage.dir_exist(experiment_dir):
            logger.error(message='Experiment id not valid', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Experiment id not valid"}
            )

        if not storage.dir_exist(cluster_dir):
            logger.error(message='Cluster id not valid', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Cluster id not valid"}
            )

        if not storage.file_exist(metadata_path):
            logger.error(message='Cluster metadata file not exist', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Cluster metadata file not exist"}
            )

        if not storage.file_exist(cluster_path):
            logger.error(message='Cluster file not exist', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Cluster file not exist"}
            )

        if not storage.file_exist(silhouette_path):
            logger.error(message='Cluster silhouette file not exist', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Cluster silhouette file not exist"}
            )

        if not storage.file_exist(scores_path):
            logger.error(message='Cluster scores file not exist', action='get_cluster', status='FAILED', resource='lse-service', userid=user_id)
            return JSONResponse(
                status_code=404,
                content={"message": "Cluster scores file not exist"}
            )
            
    elapsed = time.time() - total_time
    logger.info(message='Cluster retrieved', duration=elapsed, action='get_cluster', status='SUCCED', resource='lse-service', userid=user_id)
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

    task = tasks.cluster.apply_async(
        kwargs={
            "algorithm": cluster.algorithm,
            "params": cluster.params.dict(),
            "experiment_id": experiment_id,
            "user_id": user_id
        }
    )

    response['task_id'] = task.id

    logger.info(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
    logger.accounting(message='Posted cluster task', action='Clustering', value=1, measue="unit", resource='lse', userid=user_id)


    return response


@router.delete(
    "/experiments/{experiment_id}/clusters/{cluster_id}",
    tags=["cluster"],
    summary="Delete cluster",
    responses={
        404: {
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

    try:
        storage.delete(cluster_dir)

    except:
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

    return True
