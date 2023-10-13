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
from sklearn.metrics import silhouette_samples, calinski_harabasz_score, davies_bouldin_score

# scheduler
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from celery_app import celeryconfig

import utils.constants as constants
from utils.storage import Storage

# logging
import logging
from pythonjsonlogger import jsonlogger
import structlog

### LOGGING CONFIGURATION


#logger.info(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.warning(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.debug(message='Posted cluster task', action='Clustering', subaction=cluster.algorithm, resource='lse-service', userid=user_id)
#logger.accounting(message='Posted cluster task', action='Clustering', value=1, measure="unit", resource='lse', userid=user_id)

# Extending structlogger with custom level 'accounting'
ACCOUNTING = 15    # set to random value between DEBUG and INFO

structlog.stdlib.ACCOUNTING = ACCOUNTING
structlog.stdlib._NAME_TO_LEVEL['accounting'] = ACCOUNTING
structlog.stdlib._LEVEL_TO_NAME[ACCOUNTING] = 'accounting'

def accounting(self, *args, **kw):
    return self.log(ACCOUNTING, *args, **kw)

structlog.stdlib._FixedFindCallerLogger.accounting = accounting
structlog.stdlib.BoundLogger.accounting = accounting

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter())

logger = structlog.getLogger("json_logger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    logger.addHandler(handler)

celery = Celery()
celery.config_from_object(celeryconfig)

load_dotenv()
load_dotenv(os.getenv('ENVIRONMENT_FILE'))

storage = Storage(host=os.getenv('HOST'), storage_type=os.getenv('STORAGE_TYPE'))


@worker_process_init.connect
def init_worker(**kwargs):
    storage.connect(
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
    )
    logger.info(message='Storage client connected to nextcloud', action='storage_client_connected', status='SUCCESS', resource='lse-service', userid="celery")


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    storage.disconnect()
    logger.info(message='Storage client disconnected to nextcloud', action='storage_client_disconnected', status='SUCCESS', resource='lse-service', userid="celery")


@celery.task(name="reduction")
def reduction(algorithm, components, params, experiment_id, user_id):
    total_time = time.time()
    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        embeddings_path = os.path.join(
            experiment_dir, constants.EMBEDDINGS_FILENAME)
    else:
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
            init=params['init']
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
            n_components=components,
            affinity=params['affinity']
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
    if experiment_id.startswith('demo'):
        user_demo_dir = 'data-{}'.format(user_id)
        result_dir = os.path.join(
            experiment_dir, user_demo_dir, constants.REDUCTION_DIR, result_id)
    else:
        result_dir = os.path.join(
            user_dir, experiment_id, constants.REDUCTION_DIR, result_id)

    storage.mkdir(result_dir)

    # save reduction

    reduction_file = os.path.join(result_dir, constants.REDUCTION_FILENAME)

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

    metadata_path = os.path.join(result_dir, constants.METADATA_FILENAME)
    storage.put_file(metadata_path, json.dumps(metadata))

    elapsed = time.time() - total_time
    logger.info(message='Reduction completed and uploaded', action='reduction_completed', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
    logger.accounting(message='Computed reduction task', action='Reduction', value=(end_time - start_time)*1000, measure="time", resource='lse', userid=user_id)
    return result_id


@celery.task(name="cluster")
def cluster(algorithm, params, experiment_id, user_id):
    total_time = time.time()
    if experiment_id.startswith('demo'):
        experiment_dir = os.path.join(constants.DEMO_DIR, experiment_id)
        embeddings_path = os.path.join(
            experiment_dir, constants.EMBEDDINGS_FILENAME)
    else:
        user_dir = '{}{}'.format(constants.NEXTCLOUD_PREFIX_USER_DIR, user_id)
        embeddings_path = os.path.join(
            user_dir, experiment_id, constants.EMBEDDINGS_FILENAME)

    embeddings = json.loads(storage.get_file(embeddings_path))

    start_time = time.time()

    # calculate clusters

    if algorithm == 'dbscan':
        clusters = DBSCAN(
            eps=params['eps'],
            min_samples=params['min_samples'],
            metric=params['metric']
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
            distance_threshold=params['distance_threshold'],
            affinity=params['affinity'],
            linkage=params['linkage']
        ).fit_predict(embeddings)

    elif algorithm == 'spectral_clustering':
        clusters = SpectralClustering(
            n_clusters=params['n_clusters'],
            affinity=params['affinity'],
            n_neighbors=params['neighbors']
        ).fit_predict(embeddings)

    elif algorithm == 'optics':
        if params['min_cluster_size'] == 0:
            params['min_cluster_size'] = None

        clusters = OPTICS(
            min_samples=params['min_samples'],
            metric=params['metric'],
            cluster_method=params['cluster_method'],
            min_cluster_size=params['min_cluster_size']
        ).fit_predict(embeddings)

    elif algorithm == 'gaussian_mixture':
        clusters = GaussianMixture(
            n_components=params['n_components'],
            init_params=params['init_params'],
        ).fit_predict(embeddings)

    elif algorithm == 'birch':
        if params['n_clusters'] == 0:
            params['n_clusters'] = None

        clusters = Birch(
            n_clusters=params['n_clusters'],
            threshold=params['threshold']
        ).fit_predict(embeddings)

    # calculate silhouettes

    silhouettes = []
    if 2 <= len(set(clusters)) < len(embeddings):
        silhouettes = silhouette_samples(embeddings, clusters)
        silhouettes = silhouettes.tolist()

    # calculate scores

    scores = {}
    if 2 <= len(set(clusters)) < len(embeddings):
        scores = {
            'calinski_harabasz_score': calinski_harabasz_score(embeddings, clusters),
            'davies_bouldin_score': davies_bouldin_score(embeddings, clusters)
        }

    end_time = time.time()

    # setup result

    result_id = str(int(time.time()))
    if experiment_id.startswith('demo'):
        user_demo_dir = 'data-{}'.format(user_id)
        result_dir = os.path.join(
            experiment_dir, user_demo_dir, constants.CLUSTER_DIR, result_id)
    else:
        result_dir = os.path.join(
            user_dir, experiment_id, constants.CLUSTER_DIR, result_id)

    storage.mkdir(result_dir)

    # save clustering

    cluster_file = os.path.join(result_dir, constants.CLUSTER_FILENAME)
    storage.put_file(cluster_file, json.dumps(clusters.tolist()))

    silhouette_file = os.path.join(result_dir, constants.SILHOUETTE_FILENAME)
    storage.put_file(silhouette_file, json.dumps(silhouettes))

    scores_file = os.path.join(result_dir, constants.SCORES_FILENAME)
    storage.put_file(scores_file, json.dumps(scores))

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

    elapsed = time.time() - total_time
    logger.info(message='Clustering completed and uploaded', action='clustering_completed', status='SUCCESS', resource='lse-service', userid=user_id, duration=elapsed)
    logger.accounting(message='Computed cluster task', action='Clustering', value=(end_time - start_time)*1000, measure="time", resource='lse', userid=user_id)

    return result_id
