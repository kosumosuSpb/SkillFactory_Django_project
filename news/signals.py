from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .models import Post, User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


# сигнал на изменение связи м2м:
# при сохранении объекта модели Пост будет изменяться промежуточная таблица
# т.к. будут добавлены категории. При изменении этой таблицы через модель Поста
# будет принят сигнал и запущена эта функция.
# фактически, при создании поста будет запускаться эта функция
@receiver(m2m_changed, sender=Post.categories.through)
def email_on_create_post(**kwargs):
    # вытаскиваем объект только что сохранённого поста из кваргов
    # т.к. отправитель - модель Пост, то в инстанс приходит объект поста
    post_instance = kwargs['instance']

    # сигнал запустится два раза: перед изменениями в таблице м2м и после
    # перед изменениями будет pre_add, после изменений - post_add
    # нам нужно, чтобы сигнал запускался лишь один раз и после изменений,
    # поэтому проверяем, что в action
    model_action = kwargs['action']

    if model_action == 'post_add':
        # собираем почту всех, кто подписался на категории этой статьи
        # множество тут у меня для того, чтобы не было повторений, чтобы несколько раз не приходило одно и то же письмо
        # но на этапе формирования письма надо будет передать именно список
        subscribers_list = {user.email
                            for category in post_instance.categories.all()
                            for user in category.subscribed_users.all()}

        email_from = settings.EMAIL_FROM

        # отправка письма с превью и ссылкой на статью
        subject = 'В категориях, на которые вы подписаны появилась новая статья'
        text_message = f'В категориях, на которые вы подписаны появилась новая статья: \n\n' \
                       f'Ссылка: http://127.0.0.1:8000/posts/{post_instance.id}/\n\n' \
                       f'Заголовок: {post_instance.title}\n' \
                       f'Превью: {post_instance.preview()}\n'

        # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
        render_html_template = render_to_string('send_post.html', {'post': post_instance, 'subject': subject})
    
        # формируем письмо
        msg = EmailMultiAlternatives(subject, text_message, email_from, list(subscribers_list))
        # прикрепляем хтмл-шаблон
        msg.attach_alternative(render_html_template, 'text/html')
        # отправляем
        msg.send()


# вешаем на пост_сейв сигнал:
# при сохранении объекта модели Пост будет срабатывать этот сигнал
@receiver(post_save, sender=Post)
def post_save_post(**kwargs):  # получить параметры можно двумя способами. Первый тут
    # А можно вытащить из kwargs
    # тут вытаскиваем объект только что сохранённого поста
    post_instance = kwargs['instance']
    created = kwargs['created']

    # если статья не создана, но сохранена, значит она изменена
    if not created:
        # собираем почту всех, кто подписался на категории этой статьи
        # множество тут у меня для того, чтобы не было повторений, чтобы несколько раз не приходило одно и то же письмо
        # но на этапе формирования письма надо будет передать именно список
        subscribers_list = {user.email
                            for category in post_instance.categories.all()
                            for user in category.subscribed_users.all()}

        email_from = settings.EMAIL_FROM
    
        # отправка письма с ссылкой на статью и пометкой об изменении
        subject = 'В категориях, на которые вы подписаны была изменена статья'
        text_message = f'В категориях, на которые вы подписаны была изменена статья: \n\n' \
                       f'Ссылка: http://127.0.0.1:8000/posts/{post_instance.id}/\n\n' \
                       f'Заголовок: {post_instance.title}\n' \
                       f'Превью: {post_instance.preview()}\n'
    
        # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
        render_html_template = render_to_string('send_post.html', {'post': post_instance, 'subject': subject})
    
        # формируем письмо
        msg = EmailMultiAlternatives(subject, text_message, email_from, list(subscribers_list))
        # прикрепляем хтмл-шаблон
        msg.attach_alternative(render_html_template, 'text/html')
        # отправляем
        msg.send()


@receiver(post_save, sender=User)
def post_save_user(created, **kwargs):
    # берём объект созданного пользователя
    user_instance = kwargs['instance']
    email_from = settings.EMAIL_FROM

    # если он создан, а не изменён
    if created:
        subject = 'Приветствуем у нас на портале!'
        text_message = 'Приветственный текст'

        # рендерим в строку шаблон письма и передаём туда переменные, которые в нём используем
        render_html_template = render_to_string('hello_message.html', {'user': user_instance,
                                                                       'subject': subject,
                                                                       'text': text_message})

        # формируем письмо
        msg = EmailMultiAlternatives(subject, text_message, email_from, [user_instance.email, ])
        # прикрепляем хтмл-шаблон
        msg.attach_alternative(render_html_template, 'text/html')
        # отправляем
        msg.send()
