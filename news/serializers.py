from rest_framework import serializers
from .models import Post


class PostSerialazer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', ]
