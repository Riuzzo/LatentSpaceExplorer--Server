# "lse-${user_id}"
# "lse-${user_id}/${experiment_id}"
# "lse-${user_id}/${experiment_id}/metadata.json"
# "lse-${user_id}/${experiment_id}/embeddings.json"
# "lse-${user_id}/${experiment_id}/labels.json"
# "lse-${user_id}/${experiment_id}/images"
# "lse-${user_id}/${experiment_id}/images/${image_id}"

# "lse-${user_id}/${experiment_id}/reductions"
# "lse-${user_id}/${experiment_id}/reductions/${reduction_id}/metadata.json"
# "lse-${user_id}/${experiment_id}/reductions/${reduction_id}/reduction.json"

# "lse-${user_id}/${experiment_id}/clusters"
# "lse-${user_id}/${experiment_id}/clusters/${cluster_id}/metadata.json"
# "lse-${user_id}/${experiment_id}/clusters/${cluster_id}/cluster.json"
# "lse-${user_id}/${experiment_id}/clusters/${cluster_id}/score.json"
# "lse-${user_id}/${experiment_id}/clusters/${cluster_id}/silhouette.json"

# "lse-demo"
# "lse-demo/${experiment_id}"
# "lse-demo/${experiment_id}/data-${user_id}"
# "lse-${user_id}/${experiment_id}/metadata.json"
# "lse-${user_id}/${experiment_id}/embeddings.json"
# "lse-${user_id}/${experiment_id}/labels.json"
# "lse-${user_id}/${experiment_id}/images"
# "lse-${user_id}/${experiment_id}/images/${image_id}"

# "lse-demo/${experiment_id}/data-${user_id}"/reductions"
# "lse-demo/${experiment_id}/data-${user_id}"/reductions/${reduction_id}/metadata.json"
# "lse-demo/${experiment_id}/data-${user_id}"/reductions/${reduction_id}/reduction.json"

# "lse-demo/${experiment_id}/data-${user_id}"/clusters"
# "lse-demo/${experiment_id}/data-${user_id}"/clusters/${cluster_id}/metadata.json"
# "lse-demo/${experiment_id}/data-${user_id}"/clusters/${cluster_id}/cluster.json"
# "lse-demo/${experiment_id}/data-${user_id}"/clusters/${cluster_id}/score.json"
# "lse-demo/${experiment_id}/data-${user_id}"/clusters/${cluster_id}/silhouette.json"


NEXTCLOUD_PREFIX_USER_DIR = 'lse-'
DEMO_DIR = 'lse-demo'

EMBEDDINGS_FILENAME = 'embeddings.json'
METADATA_FILENAME = 'metadata.json'
LABELS_FILENAME = 'labels.json'
REDUCTION_FILENAME = 'reduction.json'
CLUSTER_FILENAME = 'cluster.json'
SILHOUETTE_FILENAME = 'silhouette.json'
SCORES_FILENAME = 'scores.json'

IMAGES_DIR = 'images'
REDUCTION_DIR = 'reductions'
CLUSTER_DIR = 'clusters'
