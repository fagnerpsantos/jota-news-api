from django.utils import timezone
from rest_framework import serializers
from .models import News, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class NewsSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    categories = CategorySerializer(many=True)
    is_published = serializers.BooleanField(read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'subtitle', 'image', 'content',
            'publication_date', 'author',
            'status', 'access_level', 'categories', 'created_at',
            'updated_at', 'is_published'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('status') == 'PUBLISHED' and not data.get('publication_date'):
            data['publication_date'] = timezone.now()
        return data


class NewsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'title', 'subtitle', 'image', 'content',
            'publication_date', 'status',
            'access_level', 'categories'
        ]

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        news = News.objects.create(**validated_data)
        news.categories.set(categories)
        return news