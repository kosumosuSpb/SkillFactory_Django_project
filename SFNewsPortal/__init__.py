from .celery_django import app as celery_app


# имя, которое мы дали в celery_django.py
__all__ = ('celery_app',)
