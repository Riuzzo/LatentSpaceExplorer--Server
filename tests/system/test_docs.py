from fastapi.testclient import TestClient

from main import app


client = TestClient(app, root_path="/server")


def test_docs():
    response = client.get("/docs")

    # check response status code
    assert response.status_code == 200
