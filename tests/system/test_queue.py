import os
import redis


def test_queue_connection():
    redis_host = os.environ.get("REDIS_QUEUE_SERVICE_HOST")
    redis_port = os.environ.get("REDIS_QUEUE_SERVICE_PORT")

    queue = redis.Redis(host=redis_host, port=redis_port, db=0)

    assert queue.ping()
