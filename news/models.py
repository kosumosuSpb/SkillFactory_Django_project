from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache


class Author(models.Model):
    rating = models.IntegerField(default=0)
    # cвязь «один к одному» с встроенной моделью пользователей User
    # если удалили юзера, то нет смысла оставлять автора, поэтому его тоже удаляем
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # posts - FK

    def __str__(self):
        return self.user.username

    def update_rating(self):
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

        self.rating = post_rating + comments_rating + news_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    # Фактически тут автоматом создастся атрибут posts со связью многие-ко-многим с моделью Post

    # поле для хранения подписавшихся на эту категорию пользователей
    subscribed_users = models.ManyToManyField(User, related_name='subscribed_categories')

    # posts - FK

    def __str__(self):
        return self.name


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
    # связь «многие ко многим» с моделью Category (через дополнительную модель PostCategory)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts')
    # comments - FK

    def get_categories(self):
        result = []
        for category in self.categories.all():
            result.append(category)
        return result

    def get_comments(self):
        result = []
        for comment in self.comments.all():
            result.append(comment)
        return result

    # абсолютный путь, чтобы после создания нас перебрасывало на страницу с постом
    def get_absolute_url(self):
        return f'/posts/{self.id}'

    def __str__(self):
        return f'{self.title}: {self.text[:40]}...'

    def preview(self):
        # возвращает начало статьи, длиной в 124 символа и добавляет многоточие
        return self.text[:124] + '...' if len(self.text) >= 124 else self.text + '...'

    # переопределение метода сохранения, чтобы он очищал кеш
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его

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

    def __str__(self):
        return f'{self.text[:20]}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
