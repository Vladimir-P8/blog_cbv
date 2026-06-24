from rest_framework import serializers
# from taggit.serializers import TagListSerializerField
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

from apps.blog.models import Post

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    # Явно указываем поле тегов
    tags = TagListSerializerField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        fields = (
            'id',
            "author",
            "title",
            "description",
            "text",
            "category",
            "create",
            "update",
            "fixed",
            "status",
            "slug",
            "tags",
        )
        model = Post
