import pytest
from django.urls import reverse
from rest_framework import status
from news.models import News

pytestmark = pytest.mark.django_db

class TestNewsAPI:
    def test_list_news_unauthenticated(self, api_client, published_news, draft_news):
        url = reverse('news-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # Only published news
        assert response.data['results'][0]['title'] == published_news.title
    
    def test_create_news_as_editor(self, authenticated_editor_client, category):
        url = reverse('news-list')
        data = {
            'title': 'New Test News',
            'content': 'New Test Content',
            'categories': [category.id],
            'status': 'DRAFT'
        }
        
        response = authenticated_editor_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert News.objects.filter(title='New Test News').exists()
    
    def test_create_news_as_reader(self, authenticated_reader_client, category):
        url = reverse('news-list')
        data = {
            'title': 'Reader News',
            'content': 'Reader Content',
            'categories': [category.id],
            'status': 'DRAFT'
        }
        
        response = authenticated_reader_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not News.objects.filter(title='Reader News').exists()
    
    def test_retrieve_published_news(self, api_client, published_news):
        url = reverse('news-detail', kwargs={'pk': published_news.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == published_news.title
    
    def test_retrieve_draft_news_unauthenticated(self, api_client, draft_news):
        url = reverse('news-detail', kwargs={'pk': draft_news.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_draft_news_as_author(self, authenticated_editor_client, draft_news):
        url = reverse('news-detail', kwargs={'pk': draft_news.id})
        response = authenticated_editor_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == draft_news.title

    def test_update_news_as_author(self, authenticated_editor_client, draft_news):
        url = reverse('news-detail', kwargs={'pk': draft_news.id})
        data = {
            'title': 'Updated Draft News',
            'content': draft_news.content,
            'status': 'DRAFT'
        }
        
        response = authenticated_editor_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        draft_news.refresh_from_db()
        assert draft_news.title == 'Updated Draft News'
    
    def test_publish_news(self, authenticated_editor_client, draft_news):
        url = reverse('news-publish', kwargs={'pk': draft_news.id})
        response = authenticated_editor_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        draft_news.refresh_from_db()
        assert draft_news.status == 'PUBLISHED'

    def test_filter_news_by_category(self, api_client, published_news, category):
        url = f"{reverse('news-list')}?category={category.id}"
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == published_news.title
    
    def test_search_news(self, api_client, published_news):
        url = f"{reverse('news-list')}?search={published_news.title[:5]}"
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == published_news.title