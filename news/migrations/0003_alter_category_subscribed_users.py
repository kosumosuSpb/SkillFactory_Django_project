# Generated by Django 4.0.1 on 2022-01-11 17:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0002_category_subscribed_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='subscribed_users',
            field=models.ManyToManyField(related_name='subscribed_categories', to=settings.AUTH_USER_MODEL),
        ),
    ]
