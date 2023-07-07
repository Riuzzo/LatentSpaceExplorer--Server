from fastapi.testclient import TestClient

from main import app
from utils.common import get_results_meta


client = TestClient(app, root_path='/server')


def test_api_get_reductions():
    response = client.get('/reduction')

    assert response.status_code == 200

    reductions = response.json()
    assert isinstance(reductions, list)

    if reductions:
        reduction = reductions[0]

        assert 'id' in reduction
        assert isinstance(reduction['id'], str)

        assert 'metadata' in reduction
        metadata = reduction['metadata']
        assert isinstance(metadata, dict)

        assert 'embeddings_file' in metadata
        assert isinstance(metadata['embeddings_file'], str)

        assert 'algorithm' in metadata
        assert isinstance(metadata['algorithm'], str)

        assert 'components' in metadata
        assert isinstance(metadata['components'], int)

        assert 'params' in metadata
        assert isinstance(metadata['params'], dict)

        assert 'reduction_file' in metadata
        assert isinstance(metadata['reduction_file'], str)

        assert 'start_datetime' in metadata
        assert isinstance(metadata['start_datetime'], str)

        assert 'end_datetime' in metadata
        assert isinstance(metadata['end_datetime'], str)

        assert 'seconds_elapsed' in metadata
        assert isinstance(metadata['seconds_elapsed'], int)


def test_api_get_reduction():
    reductions = get_results_meta("reduction")

    if reductions:
        reduction = reductions[0]

        response = client.get(
            '/reduction/{reduction_id}'.format(reduction_id=reduction['id']))

        assert response.status_code == 200

        results = response.json()
        assert isinstance(results, dict)

        assert reduction == results[0]


def test_api_post_reduction():
    pca = {
        'algorithm': 'pca',
        'components': 3,
        'params': {}
    }

    response = client.post('/reduction', json=pca)

    assert response.status_code == 201

    task = response.json()
    assert isinstance(task, dict)

    assert 'task_id' in task
    assert isinstance(task['task_id'], str)
