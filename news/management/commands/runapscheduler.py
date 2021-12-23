import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from collections import defaultdict
from news.models import Post
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone


logger = logging.getLogger(__name__)


# функция для рассылки писем
def send_posts(email_list, posts):
    """
    Простая функция для рассылки постов по заданным адресам

    :param email_list: один адрес почты или список адресов
    :param posts: список объектов постов для рассылки
    :return: None
    """

    # на случай, если там только один адрес, а не список
    if isinstance(email_list, str):
        subscribers_list = [email_list, ]
    else:
        subscribers_list = email_list

    email_from = settings.EMAIL_FROM  # в settings должно быть заполнено
    subject = 'В категориях, на которые вы подписаны появились новые статьи'
    text_message = 'В категориях, на которые вы подписаны появились новые статьи'

    # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
    render_html_template = render_to_string('send_posts_list.html', {'posts': posts, 'subject': subject})

    # формируем письмо
    msg = EmailMultiAlternatives(subject, text_message, email_from, list(subscribers_list))
    # прикрепляем хтмл-шаблон
    msg.attach_alternative(render_html_template, 'text/html')
    # отправляем
    msg.send()


# задача для рассылки статей за последние 7 дней по почте
# пользователя, которые подписались на категории
def send_posts_to_email_weekly():
    """
    таск который выбирает все посты, опубликованные за неделю и рассылающий
    (через вызов вспомогательной функции) их всем, кто подписан на категории, куда эти статьи входят
    :return: None
    """
    # берём посты за последние 7 дней
    # здесь мы получаем queryset
    last_week_posts_qs = Post.objects.filter(date_time__gte=datetime.now(tz=timezone.utc) - timedelta(days=7))

    # берём категории из этих постов
    # фильтруем категории по признаку того, что посты, с которыми у них связь есть в кверисете last_week_posts_qs
    # (не понадобилось, но оставил, что бы не забыть)
    # categories_qs = Category.objects.filter(posts__in=last_week_posts_qs)

    # собираем в словарь список пользователей и список постов, которые им надо разослать
    posts_for_user = defaultdict(set)  # user -> posts

    for post in last_week_posts_qs:
        for category in post.categories.all():
            for user in category.subscribed_users.all():
                posts_for_user[user].add(post)

    # непосредственно рассылка
    for user, posts in posts_for_user.items():
        send_posts(user.email, posts)


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_posts_to_email_weekly,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=00),
            # То же, что и интервал, но задача триггера таким образом более понятна django
            id="send_posts_to_email_weekly",  # уникальный id
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_posts_to_email_weekly'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить,
            # либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shutdown successfully!")