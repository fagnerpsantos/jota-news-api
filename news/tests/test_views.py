from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from news.models import News, Category
from rest_framework import status

User = get_user_model()


class NewsViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.editor = User.objects.create_user(
            username='editor',
            password='editorpass',
            role='EDITOR'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass',
            role='ADMIN'
        )
        self.reader = User.objects.create_user(
            username='reader',
            password='readerpass',
            role='READER'
        )

        self.category = Category.objects.create(name='PODER')

        self.news = News.objects.create(
            title='Published News',
            content='Published Content',
            author=self.editor,
            status='PUBLISHED',
            access_level='FREE'
        )
        self.news.categories.add(self.category)

        self.draft_news = News.objects.create(
            title='Draft News',
            content='Draft Content',
            author=self.editor,
            status='DRAFT'
        )

    def _get_auth_token(self, username, password):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': username, 'password': password},
            format='json'
        )
        return response.data['access']

    def test_list_news_unauthenticated(self):
        url = reverse('news-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Apenas publicada

    def test_create_news_as_editor(self):
        token = self._get_auth_token('editor', 'editorpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('news-list')
        data = {
            'title': 'New News',
            'content': 'New Content',
            'categories': [self.category.id],
            'status': 'DRAFT'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(News.objects.count(), 3)

    def test_create_news_as_reader(self):
        token = self._get_auth_token('reader', 'readerpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('news-list')
        data = {
            'title': 'New News',
            'content': 'New Content',
            'categories': [self.category.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publish_action(self):
        token = self._get_auth_token('editor', 'editorpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse('news-publish', kwargs={'pk': self.draft_news.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.draft_news.refresh_from_db()
        self.assertEqual(self.draft_news.status, 'PUBLISHED')

    def test_pro_content_access(self):
        pro_news = News.objects.create(
            title='PRO News',
            content='PRO Content',
            author=self.editor,
            status='PUBLISHED',
            access_level='PRO'
        )
        pro_news.categories.add(self.category)

        # Test unauthenticated access
        url = reverse('news-detail', kwargs={'pk': pro_news.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test reader access
        token = self._get_auth_token('reader', 'readerpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test admin access (should have access)
        token = self._get_auth_token('admin', 'adminpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_news_as_author(self):
        token = self._get_auth_token('editor', 'editorpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('news-detail', kwargs={'pk': self.draft_news.id})
        data = {
            'title': 'Updated News',
            'content': 'Updated Content',
            'categories': [self.category.id],
            'status': 'DRAFT'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.draft_news.refresh_from_db()
        self.assertEqual(self.draft_news.title, 'Updated News')
        
    def test_update_news_as_non_author(self):
        # Create a news item by admin
        admin_news = News.objects.create(
            title='Admin News',
            content='Admin Content',
            author=self.admin,
            status='DRAFT'
        )
        
        # Try to update as editor (not the author)
        token = self._get_auth_token('editor', 'editorpass')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('news-detail', kwargs={'pk': admin_news.id})
        data = {
            'title': 'Hacked News',
            'content': 'Hacked Content',
            'status': 'DRAFT'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
