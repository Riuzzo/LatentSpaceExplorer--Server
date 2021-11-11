from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app, root_path='/server')


def test_api_get_image():
    response = client.get('/image/000.png')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
