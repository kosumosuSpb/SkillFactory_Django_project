from django.forms import ModelForm
from .models import Post


# форма для создания поста
class PostForm(ModelForm):
    # пишем модель, которую надо использовать
    # и поля, которые нужны в форме
    class Meta:
        model = Post
        fields = ['title', 'text', 'categories', 'type', 'author']
