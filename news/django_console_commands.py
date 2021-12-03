"""
команды для ввода в консоли джанго

"""

from news.models import *

# Создать двух пользователей (с помощью метода User.objects.create_user('username'))
user1 = User.objects.create_user('user1')
user2 = User.objects.create_user('user2')

# Создать два объекта модели Author, связанные с пользователями.
author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

# Добавить 4 категории в модель Category.
category1 = Category.objects.create(name='category1')
category2 = Category.objects.create(name='category2')
category3 = Category.objects.create(name='category3')
category4 = Category.objects.create(name='category4')

# Добавить 2 статьи и 1 новость.
post1 = Post.objects.create(type='article', title='title1', text='text1 '*40, author=author1)
post2 = Post.objects.create(type='article', title='title2', text='text2 '*50, author=author2)
post3 = Post.objects.create(type='news', title='title3', text='news '*10, author=author1)

# Присвоить им категории (как минимум в одной статье/новости должно быть не меньше 2 категорий).
post1.categories.set([category1, category2])
post2.categories.set([category1, category2, category3])
post3.categories.set([category3, category4])

# Создать как минимум 4 комментария к разным объектам модели Post
# (в каждом объекте должен быть как минимум один комментарий).
comment1 = Comment.objects.create(text='comment1 '*5, post=post1, user=user2)
comment2 = Comment.objects.create(text='comment2 to comment1', post=post1, user=user1)
comment3 = Comment.objects.create(text='comment3 '*10, post=post2, user=user1)
comment4 = Comment.objects.create(text='comment4 '*10, post=post3, user=user2)
comment5 = Comment.objects.create(text='comment5 to comment 4', post=post3, user=user1)

# Применяя функции like() и dislike() к статьям/новостям и комментариям, скорректировать рейтинги этих объектов.
post1.like()
post1.like()
post1.like()
post2.dislike()
post2.dislike()
post3.dislike()
post3.dislike()
post3.like()
post3.like()
comment1.like()
comment2.dislike()
comment3.like()
comment3.like()
comment3.like()
comment3.dislike()
comment4.like()
comment5.like()
comment5.like()

# Обновить рейтинги пользователей.
author1.update_rating()
author2.update_rating()

# Вывести username и рейтинг лучшего пользователя (применяя сортировку и возвращая поля первого объекта).
best_author = Author.objects.order_by('-rating').values('user__username', 'rating').first()
# >>>best_author
# {'user__username': 'user1', 'rating': 15}

# Вывести дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи,
# основываясь на лайках/дислайках к этой статье.
# (здесь в ТЗ крайне не внятно есть намёк на то, что это должна быть именно статья, а не новость)
best_article = Post.objects.filter(type='article').order_by('-rating').first()

# выводим автора лучшей статьи отдельно
best_article.author.user.username
# 'user1'

# можно через принт вывести юзернейм, рейтинг, заголовок и превью лучшей статьи
# (просто почему бы и нет, как именно это должно выводиться в задании не указано)
print(best_article.author.user.username, best_article.rating, best_article.title, best_article.preview(), sep=', ')
# user1, 3, title1, text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text1 text...

# Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье
# вывожу через цикл для разнообразия и читаемости
for comment in best_article.comments.all(): print(comment.date_time, comment.rating, comment.text, sep=', ')
# 2021-11-21 15:54:28.326737+00:00, 1, comment1 comment1 comment1 comment1 comment1
# 2021-11-21 15:54:59.350315+00:00, -1, comment2 to comment1

# Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье
# (вывожу то же самое, но через запрос)
Comment.objects.filter(post=best_article).all().values('date_time', 'rating', 'text')
# <QuerySet [{'date_time': datetime.datetime(2021, 11, 21, 15, 54, 28, 326737, tzinfo=<UTC>), 'rating': 1, 'text': 'comment1 comment1 comment1 comment1 comment1 '}, {'date_time': datetime.datetime(2021, 11, 21, 15, 54, 59, 350315, tzinfo=<UTC>), 'rating': -1, 'text': 'comment2 to comment1'}]>
