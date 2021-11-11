from src.models.requests.clustering import AffinityPropagationModel, DBSCANModel, KMeansModel, AgglomerativeClusteringModel


# affinity propagation

def test_clustering_model_affinity_propagation():
    """ 
    Test affinity propagation: give right params to compute affinity propagation.
    Should instantiate the Affinity Propagation model
    """

    clustering = {
        "algorithm": "affinity_propagation",
        "params": {}
    }

    assert isinstance(AffinityPropagationModel.parse_obj(
        clustering), AffinityPropagationModel)


# dbscan

def test_clustering_model_dbscan():
    """ 
    Test dbscan: give right params to compute dbscan.
    Should instantiate the DBSCAN model
    """

    clustering = {
        "algorithm": "dbscan",
        "params": {
            "eps": 0.5,
            "min_samples": 10
        }
    }

    assert isinstance(DBSCANModel.parse_obj(clustering), DBSCANModel)


# kmeans

def test_clustering_model_kmeans():
    """ 
    Test kmeans: give right params to compute kmeans.
    Should instantiate the KMeans model
    """

    clustering = {
        "algorithm": "kmeans",
        "params": {
            "n_clusters": 10
        }
    }

    assert isinstance(KMeansModel.parse_obj(clustering), KMeansModel)


# agglomerative clustering

def test_clustering_model_agglomerative_clustering():
    """ 
    Test agglomerative clustering: give right params to compute agglomerative clustering.
    Should instantiate the Agglomerative Clustering model
    """

    clustering = {
        "algorithm": "agglomerative_clustering",
        "params": {
            "distance_threshold": 10
        }
    }

    assert isinstance(AgglomerativeClusteringModel.parse_obj(
        clustering), AgglomerativeClusteringModel)
