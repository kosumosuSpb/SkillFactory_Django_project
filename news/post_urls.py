from django.urls import path
from .views import PostList, PostDetail


# т. к. сам по себе это класс, то нам надо представить этот класс в виде view.
# Для этого вызываем метод as_view
urlpatterns = [path('', PostList.as_view()),
               path('<int:pk>', PostDetail.as_view()),  # pk - первичный ключ. Для вывода отдельной статьи

               ]