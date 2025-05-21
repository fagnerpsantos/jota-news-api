from django.test import TestCase
from django.contrib.auth import get_user_model
from news.models import News, Category
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class NewsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='EDITOR'
        )
        self.category = Category.objects.create(name='PODER')

        self.news = News.objects.create(
            title='Test News',
            content='Test Content',
            author=self.user,
            status='DRAFT'
        )
        self.news.categories.add(self.category)

    def test_news_creation(self):
        self.assertEqual(self.news.title, 'Test News')
        self.assertEqual(self.news.author, self.user)
        self.assertEqual(self.news.status, 'DRAFT')
        self.assertEqual(self.news.categories.count(), 1)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Poder')
        
    def test_news_str(self):
        self.assertEqual(str(self.news), 'Test News')
        
    def test_news_ordering(self):
        # Create a second news item with an earlier publication date
        earlier_news = News.objects.create(
            title='Earlier News',
            content='Earlier Content',
            author=self.user,
            status='PUBLISHED',
            publication_date=timezone.now() - timedelta(days=1)
        )
        
        # Get all news ordered by default ordering (-publication_date)
        news_list = News.objects.all()
        
        # The first item should be the most recent one
        self.assertEqual(news_list[0], self.news)
        self.assertEqual(news_list[1], earlier_news)
        
    def test_access_level_default(self):
        self.assertEqual(self.news.access_level, 'FREE')
        
    def test_news_with_image(self):
        # Test that a news item can be created with an image
        news_with_image = News.objects.create(
            title='News With Image',
            content='Content with image',
            author=self.user,
            status='DRAFT',
            image='path/to/test/image.jpg'
        )
        self.assertEqual(news_with_image.image, 'path/to/test/image.jpg')
