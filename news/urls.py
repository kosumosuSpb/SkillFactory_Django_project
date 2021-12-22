from django.urls import path
from .views import NewsList, PostList, PostDetail, FilterPostView, \
                   PostCreateView, PostUpdateView, PostDeleteView, subscribe_category

# т. к. сам по себе это класс, то нам надо представить этот класс в виде view.
# Для этого вызываем метод as_view
urlpatterns = [path('', PostList.as_view()),
               path('<int:pk>/', PostDetail.as_view(), name='post'),  # pk - первичный ключ.
               path('news/', NewsList.as_view(), name='news'),
               path('search/', FilterPostView.as_view()),
               path('add/', PostCreateView.as_view(), name='post_create'),
               path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
               path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
               path('subscribe/', subscribe_category),  # url для ссылки на метод подписки на категорию

               ]
