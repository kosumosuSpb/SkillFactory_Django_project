from celery import shared_task
from sf_news_project.celery import app as celery_app

from django.conf import settings

from collections import defaultdict
from news.models import Post
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone


@celery_app.task
def test_task():
    print('=== its the test task --->')


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
# можно и celery_app.task и shared_task, но предпочтительно вроде второе
@shared_task()
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
