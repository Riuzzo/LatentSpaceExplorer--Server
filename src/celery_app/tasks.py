import os
import time
import json
from dotenv import load_dotenv

# reduction algorithms
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE, SpectralEmbedding, Isomap, MDS
from umap import UMAP

# clustering algorithm
from sklearn.cluster import DBSCAN, AffinityPropagation, KMeans, AgglomerativeClustering, SpectralClustering, OPTICS, Birch
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_samples

# scheduler
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from src.celery_app import celeryconfig

import src.utils.constants as constants
from src.utils.storage import Storage


celery = Celery()
celery.config_from_object(celeryconfig)

load_dotenv()
load_dotenv(os.getenv('ENVIRONMENT_FILE'))

storage = Storage(host=os.getenv('NEXCLOUD_HOST'))


@worker_process_init.connect
def init_worker(**kwargs):
    storage.connect(
        user=os.getenv('NEXCLOUD_USER'),
        password=os.getenv('NEXCLOUD_PASSWORD'),
    )


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    storage.disconnect()


@celery.task(name="reduction")
def reduction(algorithm, components, params, experiment_id, user_id):
    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    embeddings_path = os.path.join(
        user_dir, experiment_id, constants.EMBEDDINGS_FILENAME)
    embeddings = json.loads(storage.get_file(embeddings_path))

    start_time = time.time()

    # calculate reduction

    if algorithm == 'pca':
        reduction = PCA(
            n_components=components
        ).fit_transform(embeddings)

    elif algorithm == 'tsne':
        reduction = TSNE(
            n_components=components,
            perplexity=params['perplexity'],
            n_iter=params['iterations'],
            learning_rate=params['learning_rate'],
            metric=params['metric'],
            init='pca'
        ).fit_transform(embeddings)

    elif algorithm == 'umap':
        reduction = UMAP(
            n_components=components,
            n_neighbors=params['neighbors'],
            min_dist=params['min_distance'],
            metric=params['metric'],
            densmap=params['densmap']
        ).fit_transform(embeddings)

    elif algorithm == 'truncated_svd':
        reduction = TruncatedSVD(
            n_components=components,
        ).fit_transform(embeddings)

    elif algorithm == 'spectral_embedding':
        reduction = SpectralEmbedding(
            n_components=components
        ).fit_transform(embeddings)

    elif algorithm == 'isomap':
        reduction = Isomap(
            n_components=components,
            n_neighbors=params['neighbors'],
            metric=params['metric']
        ).fit_transform(embeddings)

    elif algorithm == 'mds':
        reduction = MDS(
            n_components=components
        ).fit_transform(embeddings)

    end_time = time.time()

    # setup result

    result_id = str(int(time.time()))
    result_dir = os.path.join(
        user_dir, experiment_id, constants.REDUCTION_DIR, result_id)

    storage.mkdir(result_dir)

    # save reduction

    reduction_file = os.path.join(result_dir, 'reduction.json')

    storage.put_file(reduction_file, json.dumps(reduction.tolist()))

    # save metadata

    metadata = {
        'algorithm': algorithm,
        'components': components,
        'params': params,
        'start_datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time)),
        'end_datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(end_time)),
        'seconds_elapsed': int(end_time - start_time)
    }

    metadata_path = os.path.join(result_dir, 'metadata.json')
    storage.put_file(metadata_path, json.dumps(metadata))

    return result_id


@celery.task(name="cluster")
def cluster(algorithm, params, experiment_id, user_id):
    user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)

    embeddings_path = os.path.join(
        user_dir, experiment_id, constants.EMBEDDINGS_FILENAME)
    embeddings = json.loads(storage.get_file(embeddings_path))

    start_time = time.time()

    # calculate clusters

    if algorithm == 'dbscan':
        clusters = DBSCAN(
            eps=params['eps'],
            min_samples=params['min_samples']
        ).fit_predict(embeddings)

    elif algorithm == 'affinity_propagation':
        clusters = AffinityPropagation().fit_predict(embeddings)

    elif algorithm == 'kmeans':
        clusters = KMeans(
            n_clusters=params['n_clusters']
        ).fit_predict(embeddings)

    elif algorithm == 'agglomerative_clustering':
        clusters = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=params['distance_threshold']
        ).fit_predict(embeddings)

    elif algorithm == 'spectral_clustering':
        clusters = SpectralClustering(
            n_clusters=params['n_clusters']
        ).fit_predict(embeddings)

    elif algorithm == 'optics':
        clusters = OPTICS(
            min_samples=params['min_samples'],
            metric=params['metric'],
        ).fit_predict(embeddings)

    elif algorithm == 'gaussian_mixture':
        clusters = GaussianMixture(
            n_components=params['n_components'],
        ).fit_predict(embeddings)

    elif algorithm == 'birch':
        clusters = Birch(
            n_clusters=params['n_clusters'],
        ).fit_predict(embeddings)

    # calculate silhouettes

    if 2 <= len(set(clusters)) <= len(embeddings) - 1:
        silhouettes = silhouette_samples(embeddings, clusters)
        silhouettes = silhouettes.tolist()
    else:
        silhouettes = []

    end_time = time.time()

    # setup result

    result_id = str(int(time.time()))
    result_dir = os.path.join(
        user_dir, experiment_id, constants.CLUSTER_DIR, result_id)

    storage.mkdir(result_dir)

    # save clustering

    cluster_file = os.path.join(result_dir, constants.CLUSTER_FILENAME)
    storage.put_file(cluster_file, json.dumps(clusters.tolist()))

    silhouette_file = os.path.join(result_dir, constants.SILHOUETTE_FILENAME)
    storage.put_file(silhouette_file, json.dumps(silhouettes))

    # save metadata

    metadata = {
        'algorithm': algorithm,
        'params': params,
        'start_datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time)),
        'end_datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time)),
        'seconds_elapsed': int(end_time - start_time)
    }

    metadata_path = os.path.join(result_dir, constants.METADATA_FILENAME)
    storage.put_file(metadata_path, json.dumps(metadata))

    return result_id
