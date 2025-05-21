import pytest
from django.contrib.auth import get_user_model
from news.models import News, Category
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def editor_user():
    return User.objects.create_user(
        username='editor',
        email='editor@example.com',
        password='editorpass',
        role='EDITOR'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass',
        role='ADMIN'
    )

@pytest.fixture
def reader_user():
    return User.objects.create_user(
        username='reader',
        email='reader@example.com',
        password='readerpass',
        role='READER'
    )

@pytest.fixture
def category():
    return Category.objects.create(name='PODER')

@pytest.fixture
def published_news(editor_user, category):
    news = News.objects.create(
        title='Published News',
        content='Published Content',
        author=editor_user,
        status='PUBLISHED',
        publication_date=timezone.now(),
        access_level='FREE'
    )
    news.categories.add(category)
    return news

@pytest.fixture
def draft_news(editor_user):
    return News.objects.create(
        title='Draft News',
        content='Draft Content',
        author=editor_user,
        status='DRAFT'
    )

@pytest.fixture
def pro_news(editor_user, category):
    news = News.objects.create(
        title='PRO News',
        content='PRO Content',
        author=editor_user,
        status='PUBLISHED',
        publication_date=timezone.now(),
        access_level='PRO'
    )
    news.categories.add(category)
    return news

@pytest.fixture
def scheduled_news(editor_user):
    return News.objects.create(
        title='Scheduled News',
        content='Scheduled Content',
        author=editor_user,
        status='PUBLISHED',
        scheduled_date=timezone.now() + timezone.timedelta(days=1),
        is_published=False
    )

@pytest.fixture
def editor_token(editor_user):
    refresh = RefreshToken.for_user(editor_user)
    return str(refresh.access_token)

@pytest.fixture
def admin_token(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)

@pytest.fixture
def reader_token(reader_user):
    refresh = RefreshToken.for_user(reader_user)
    return str(refresh.access_token)

@pytest.fixture
def authenticated_editor_client(api_client, editor_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {editor_token}')
    return api_client

@pytest.fixture
def authenticated_admin_client(api_client, admin_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    return api_client

@pytest.fixture
def authenticated_reader_client(api_client, reader_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {reader_token}')
    return api_client