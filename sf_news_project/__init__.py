from .celery import app as celery_app


# имя, которое мы дали в celery.py
__all__ = ('celery_app',)
