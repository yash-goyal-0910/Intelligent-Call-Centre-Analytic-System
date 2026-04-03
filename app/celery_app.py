from celery import Celery
import os

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Initialize celery app
celery_app = Celery(
    "analytics_worker",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

# Autodiscover tasks from app.tasks
celery_app.autodiscover_tasks(['app'])
