from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    rating = models.IntegerField(default=0)
    # cвязь «один к одному» с встроенной моделью пользователей User
    # если удалили юзера, то нет смысла оставлять автора, поэтому его тоже удаляем
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # самый оптимальный вариант метода, т.к. самый быстрый, но не самый простой
    # все основные рассчёты делаются на стороне БД за счёт использования aggregate
    def update_rating(self):
        # загадочный метод:
        # суммарный рейтинг каждой статьи автора * 3
        # получим готовый словарь с суммой рейтингов всех постов автора
        # {'x': int}  (если не указать x=, то название будет по умолчанию rating__sum)
        # икс тут только потому что так лаконичнее его подставить в конец строки
        post_rating = Post.objects.filter(author=self).aggregate(x=models.Sum('rating') * 3)['x']

        # суммарный рейтинг всех комментариев автора
        comments_rating = Comment.objects.filter(user=self.user).aggregate(x=models.Sum('rating'))['x']

        # суммарный рейтинг всех комментариев к статьям автора
        # получаем все комментарии, написанные к постам конкретного автора
        news_comments = Comment.objects.filter(post__author=self).aggregate(x=models.Sum('rating'))['x']

        self.rating = post_rating + comments_rating + news_comments
        self.save()

    # второй вариант метода:
    # чуть более читаемый и понятный, но самый медленный (по идее)
    def update_rating_2(self):
        # загадочный метод:
        # суммарный рейтинг каждой статьи автора * 3
        post_rating = Post.objects.filter(author=self).values('rating')  # получим список объектов со словарями
        # пройдёмся по списку, вытащим каждый словарь и у него - по ключу обратимся к значению
        post_rating = sum(rate['rating'] for rate in post_rating) * 3

        # суммарный рейтинг всех комментариев автора
        comments_rating = Comment.objects.filter(user=self.user).values('rating')  # получим список объектов со словарями
        comments_rating = sum(rate['rating'] for rate in comments_rating)

        # суммарный рейтинг всех комментариев к статьям автора
        # получаем все комментарии, написанные к постам конкретного автора
        news_comments = Comment.objects.filter(post__author=self)
        # получаем сумму рейтингов комментариев к постам этого автора
        news_comments_rating = sum(comment.rating for comment in news_comments)

        self.rating = sum([post_rating, comments_rating, news_comments_rating])
        self.save()

    # этот вариант был использован в задании для сдачи в SF
    # основное отличие от предыдущего в том, что сначала обращается к Post, фильтрует по автору
    # после обращается по связи к комментам и получает только их рейтинги в виде списка словарей (внутри QuerySet)
    # после чего итерируем этот список и обращаемся по ключу к рейтингу, потом всё складываем
    def update_rating_old(self):
        # загадочный метод:
        # суммарный рейтинг каждой статьи автора * 3
        post_rating = Post.objects.filter(author=self).values('rating')  # получим список объектов со словарями
        # пройдёмся по списку, вытащим каждый словарь и у него - по ключу обратимся к значению
        post_rating = sum(rate['rating'] for rate in post_rating) * 3

        # суммарный рейтинг всех комментариев автора
        comments_rating = Comment.objects.filter(user=self.user).values('rating')  # получим список объектов со словарями
        comments_rating = sum(rate['rating'] for rate in comments_rating)

        # суммарный рейтинг всех комментариев к статьям автора
        news_comments_rating = Post.objects.filter(author=self).values('comments__rating')
        news_comments_rating = sum(rate['comments__rating'] for rate in news_comments_rating)

        self.rating = sum([post_rating, comments_rating, news_comments_rating])
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    # Фактически тут автоматом создастся атрибут posts со связью многие-ко-многим с моделью Post


class Post(models.Model):
    # список кортежей: первая строка - то, что хранится в базе, вторая - то, что отображается в админке
    TYPES = [('article', 'Статья'), ('news', 'Новость')]
    type = models.CharField(max_length=15, choices=TYPES, default='article')
    date_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    # связь один ко многим с моделью Author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    # связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts')

    def preview(self):
        # возвращает начало статьи, длиной в 124 символа и добавляет многоточие
        return self.text[:124] + '...' if len(self.text) >= 124 else self.text + '...'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


# эта модель создаётся автоматически, вручную её создавать фактически не нужно
class PostCategory(models.Model):
    # связь один ко многим с моделью Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # связь один ко многим с моделью Categories
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField(max_length=500)
    date_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    # связь один ко многим с моделью Post
    # related_name задаёт имя атрибута, который создаётся автоматически
    # при создании связи от комментария к посту в данном случае.
    # По умолчанию атрибут назывался бы comment_set
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # связь один ко многим с моделью User (комментарии могу оставлять все, не только авторы)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
