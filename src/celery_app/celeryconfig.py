import os

REDIS_HOST = os.environ.get("REDIS_QUEUE_SERVICE_HOST")
REDIS_PORT = os.environ.get("REDIS_QUEUE_SERVICE_PORT")


broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}"
result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}"

result_extended = True
result_expires = 600

imports = ('celery_app.tasks', )
