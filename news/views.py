from django.shortcuts import render  # на фиг не нужно
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin  # проверка авторизации и прав доступа
from .filters import PostFilter  # импорт фильтра для представления страницы с фильтрами статей
from .models import Post, Category  # импорт моделей поста и категорий
from .forms import PostForm


# вывод всех постов
class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    form_class = PostForm  # чтобы получить доступ к форме через POST
    paginate_by = 10  # постраничный вывод по 10

    # общий метод для создания дополнительных атрибутов
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        context['is_not_author'] = not self.request.user.groups.filter(name='author').exists()
        context['is_auth'] = self.request.user.is_authenticated
        return context

    # переопределение метода чтобы хз что,
    # зачем это вообще всё? почему по-умолчанию всё не работает как надо?
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса

        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый пост
            form.save()

        return super().get(request, *args, **kwargs)


# для страницы с фильтром (поиск)
class FilterPostView(ListView):
    model = Post
    template_name = 'posts_filter.html'
    context_object_name = 'posts_filter'
    paginate_by = 10

    # общий метод для создания дополнительных атрибутов
    # (где-то во views уже был, надо разобраться вообще как это работает, ибо я хз)
    def get_context_data(self, **kwargs):
        # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        # на самом деле не понятно вообще ничего. Что происходит то?
        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст (что бы это ни значило)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


# для вывода одного отдельного поста
class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


# создание поста. Указываем шаблон и форму ввода
class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post',)


# редактирование поста
class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    # метод get_object мы используем вместо queryset,
    # чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# удаление поста
class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()  # это вот зачем? что происходит? у нас же удаление тут, что за вывод всех постов?
    success_url = '/posts/'
    permission_required = ('news.delete_post',)


# для вывода только новостей
class NewsList(ListView):
    model = Post
    template_name = 'news_posts.html'
    context_object_name = 'news_posts'
    queryset = Post.objects.filter(type='news')
    paginate_by = 10
