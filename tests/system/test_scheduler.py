from src.celery_app.tasks import celery


def test_scheduler():
    inspect = celery.control.inspect()
    nodes = inspect.stats()

    assert nodes


def test_scheduler_worker():
    workers = celery.control.ping()
    assert isinstance(workers, list)

    assert workers
