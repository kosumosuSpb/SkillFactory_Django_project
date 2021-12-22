from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    # подключаем сигналы
    def ready(self):
        import news.signals
        from .tasks import send_posts_to_email_weekly  # из тасков задача по рассылке

        # импорт триггеров
        from apscheduler.triggers.combining import OrTrigger
        from apscheduler.triggers.cron import CronTrigger

        # импорт расписания
        from .scheduler import post_subscribe_scheduler

        # сборка триггера
        trigger = OrTrigger([CronTrigger(day_of_week='sat', hour=12), ])

        # добавление задачи
        post_subscribe_scheduler.add_job(send_posts_to_email_weekly, trigger)
