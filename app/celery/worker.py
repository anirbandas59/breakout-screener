from app.celery import celery_app

# Import tasks to register them with Celery
from app.tasks import *
