import os
from celery import Celery
from celery.schedules import crontab
from celery import shared_task
from django.conf import settings


# этот код скопирован с manage.py
# он установит модуль настроек по умолчанию Django для приложения 'celery'.
# sf_news_project.settings - имя_проекта.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sf_news_project.settings')

# Создаем объект (экземпляр класса) celery и даем ему имя
# celery -A sf_news_project worker -l info -P eventlet
# celery -A sf_news_project beat -l INFO
# запускать из под папки проекта, выше сеттингзов
app = Celery('sf_news_project')

# Загружаем config с настройками для объекта celery.
# т.е. импортируем настройки из django файла settings
# namespace='CELERY' - в данном случае говорит о том, что применятся будут только
# те настройки из файла settings.py которые начинаются с ключевого слова CELERY
app.config_from_object('django.conf:settings', namespace="CELERY")

# расписание
# надо ещё разобраться где джанге указать временную зону, потому что он работает в UTC 0
# видимо, по умолчанию (приходилось время писать -3 часа)
app.conf.beat_schedule = {
    'email_every_monday_8am': {
        'task': 'news.tasks.send_posts_to_email_weekly',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
        # 'args': (agrs),
    },
    # TEST TASK FOR DEBUG
    # 'test_task': {
    #     'task': 'news.tasks.test_task',
    #     'schedule': 5,
    # }
}

app.autodiscover_tasks()
