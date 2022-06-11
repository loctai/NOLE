from app import app
from .make_celery import make_celery
celery = make_celery(app)