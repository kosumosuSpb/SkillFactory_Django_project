from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


# импорт класса формы из allauth и переопределение функции сохранения,
# которая выполняется при успешном заполнении формы регистрации.
# авто добавление пользователя в группу common при регистрации
class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
