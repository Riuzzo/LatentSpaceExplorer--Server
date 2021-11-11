from fastapi.testclient import TestClient

from src.main import app
from src.utils.common import get_results_meta


client = TestClient(app, root_path='/server')


def test_api_get_clusterings():
    response = client.get('/clustering')

    assert response.status_code == 200

    clusterings = response.json()
    assert isinstance(clusterings, list)

    if clusterings:
        reduction = clusterings[0]

        assert 'id' in reduction
        assert isinstance(reduction['id'], str)

        assert 'metadata' in reduction
        metadata = reduction['metadata']
        assert isinstance(metadata, dict)

        assert 'embeddings_file' in metadata
        assert isinstance(metadata['embeddings_file'], str)

        assert 'algorithm' in metadata
        assert isinstance(metadata['algorithm'], str)

        assert 'params' in metadata
        assert isinstance(metadata['params'], dict)

        assert 'clustering_file' in metadata
        assert isinstance(metadata['clustering_file'], str)

        assert 'start_datetime' in metadata
        assert isinstance(metadata['start_datetime'], str)

        assert 'end_datetime' in metadata
        assert isinstance(metadata['end_datetime'], str)

        assert 'seconds_elapsed' in metadata
        assert isinstance(metadata['seconds_elapsed'], int)


def test_api_get_clustering():
    clusterings = get_results_meta("clustering")

    if clusterings:
        clustering = clusterings[0]

        response = client.get(
            '/clustering/{clustering_id}'.format(clustering_id=clustering['id']))

        assert response.status_code == 200

        results = response.json()
        assert isinstance(results, dict)

        assert clustering == results[0]


def test_api_post_clustering():
    affinity_propagation = {
        'algorithm': 'affinity_propagation',
        'params': {}
    }

    response = client.post('/clustering', json=affinity_propagation)

    assert response.status_code == 201

    task = response.json()
    assert isinstance(task, dict)

    assert 'task_id' in task
    assert isinstance(task['task_id'], str)
