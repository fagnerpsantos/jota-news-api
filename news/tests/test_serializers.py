from django.test import TestCase
from news.serializers import NewsSerializer, NewsCreateSerializer, CategorySerializer
from news.models import News, Category
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class NewsSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='EDITOR'
        )
        self.category = Category.objects.create(name='PODER')
        self.news_data = {
            'title': 'Test News',
            'content': 'Test Content',
            'author': self.user.id,
            'categories': [self.category.id],
            'status': 'DRAFT'
        }

    def test_serializer_without_required_fields(self):
        invalid_data = self.news_data.copy()
        invalid_data.pop('title')
        serializer = NewsCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_with_invalid_status(self):
        invalid_data = self.news_data.copy()
        invalid_data['status'] = 'INVALID'
        serializer = NewsCreateSerializer(data=invalid_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            
    def test_news_serializer_read(self):
        news = News.objects.create(
            title='Test News',
            content='Test Content',
            author=self.user,
            status='PUBLISHED',
            publication_date=timezone.now()
        )
        news.categories.add(self.category)
        
        serializer = NewsSerializer(news)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test News')
        self.assertEqual(data['content'], 'Test Content')
        self.assertEqual(data['author'], str(self.user))
        self.assertEqual(data['status'], 'PUBLISHED')
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], 'PODER')

    def test_category_serializer(self):
        serializer = CategorySerializer(self.category)
        data = serializer.data
        
        self.assertEqual(data['id'], self.category.id)
        self.assertEqual(data['name'], 'PODER')