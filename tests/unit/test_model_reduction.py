from models.requests.reduction import PCAModel, TSNEModel, UMAPModel


# pca

def test_reduction_model_pca():
    """ 
    Test pca: give right params to compute pca.
    Should instantiate the PCA model
    """

    reduction = {
        "algorithm": "pca",
        "components": 2,
        "params": {}
    }

    assert isinstance(PCAModel.parse_obj(reduction), PCAModel)


# tsne

def test_reduction_model_tsne():
    """ 
    Test tsne: give right params to compute tsne.
    Should instantiate an TSNE model
    """

    reduction = {
        "algorithm": "tsne",
        "components": 2,
        "params": {
            "perplexity": 10,
            "iterations": 500,
            "learning_rate": 1000
        }
    }

    assert isinstance(TSNEModel.parse_obj(reduction), TSNEModel)


# umap

def test_reduction_model_umap():
    """ 
    Test umap: give right params to compute umap.
    Should instantiate an UMAP model
    """

    reduction = {
        "algorithm": "umap",
        "components": 2,
        "params": {
            "neighbors": 10,
            "min_distance": 0.5
        }
    }

    assert isinstance(UMAPModel.parse_obj(reduction), UMAPModel)
