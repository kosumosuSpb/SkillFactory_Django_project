import os
from celery import Celery
from celery.schedules import crontab
from celery import shared_task


# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
# SFNewsPortal.settings - имя_проекта.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SFNewsPortal.settings')

# Создаем объект(экземпляр класса) celery и даем ему имя
# оно будет указываться при запуске celery в терминале:
# celery_django -A celery_app worker -l INFO
# и в __init__
app = Celery('celery_app')

# Загружаем config с настройками для объекта celery.
# т.е. импортируем настройки из django файла settings
# namespace='CELERY' - в данном случае говорит о том, что применятся будут только
# те настройки из файла settings.py которые начинаются с ключевого слова CELERY
app.config_from_object('django.conf:settings')

# загрузка tasks.py в приложение django
# app.autodiscover_tasks()

# from django.conf import settings
app.autodiscover_tasks()


# расписание
app.conf.beat_schedule = {
    'email_every_monday_8am': {
        'task': 'news.board.tasks.send_posts_to_email_weekly',
        'schedule': crontab(hour=13, minute=38, day_of_week='tuesday'),
        # 'args': (agrs),
    },
    'test_task': {
        'task': 'test_task',
        'schedule': 5,
    }
}


@shared_task()
def test_task():
    print('=== its the test task --->')


# DEBUG
print('1')
