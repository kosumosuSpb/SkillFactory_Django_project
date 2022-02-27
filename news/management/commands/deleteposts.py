from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category


class Command(BaseCommand):
    # показывает подсказку при вводе "python manage.py <команда> --help"
    help = 'Подсказка вашей команды'
    missing_args_message = 'Недостаточно аргументов'

    # напоминать ли о миграциях. Если true — то будет напоминание о том, что не сделаны все миграции (если такие есть)
    requires_migrations_checks = True

    def add_arguments(self, parser):
        # Позиционные аргументы (метод add_argument наследуется от BaseCommand)
        parser.add_argument('category',  # пришедший аргумент будет сохранён под ключом category в словаре option
                            type=str)  # приведение аргумента к указанному типу

        """
        choices — ограничение вариантов значения аргумента. 
                В значение choices передается список возможных значений
        
        required — обязательный аргумент.
        
        help — Описание того, что делает данный аргумент.
        
        dest — если вы хотите сохранить вашу опцию под другим именем, можете указать dest='my_new_name'. 
                В противном случае будет использовано имя аргумента (тут не очень понятно с именем)
        Эти аргументы будут далее переданы функцию handle в виде словаря options
        
        nargs= '+' - количество аргументов: 
                ? - 1 или default, 
                + - хотя бы 1, если несколько — собираются в список, 
                * - — все сколько есть, и собираются в список
                
                Обратите внимание: если вы используете этот аргумент, то значение вашей опции из командной строки будет 
                передаваться в handle в виде списка, даже если там всего один элемент. 
                (При этом дефолтное значение передается как есть, без приведения к списку.
        """

    def handle(self, *args, **options):
        answer = input(f'Вы правда хотите удалить все статьи в категории {options["category"]}? yes/no > ')

        # просто добавил ещё один вариант
        if answer not in ('yes', 'y'):
            self.stdout.write(self.style.ERROR('Отменено'))
            return

        try:
            # выбираем категорию по имени, которое берём из словаря options
            # (именованные аргументы, которые передаются в функцию)
            category = Category.objects.get(name=options['category'])

        # в случае, если категории с таким названием не найдено:
        except Category.DoesNotExist:
            raise CommandError(f'Could not find category {options["category"]}')

        # выбираем все посты, которые соответствуют этой категории и удаляем
        Post.objects.filter(categories=category).delete()

        # если всё ок - выводим сообщение
        self.stdout.write(self.style.SUCCESS(
            f'Successfully deleted all news from category {category.name}'))
