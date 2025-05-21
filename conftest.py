import pytest
import django

# Configurar o Django antes de importar os modelos
try:
    django.setup()
except:  # noqa
    pass

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def editor_user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='editor',
        email='editor@example.com',
        password='editorpass',
        role='EDITOR'
    )

@pytest.fixture
def admin_user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass',
        role='ADMIN'
    )

@pytest.fixture
def reader_user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='reader',
        email='reader@example.com',
        password='readerpass',
        role='READER'
    )

@pytest.fixture
def category():
    from news.models import Category
    return Category.objects.create(name='PODER')

@pytest.fixture
def published_news(editor_user, category):
    from news.models import News
    from django.utils import timezone
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
    from news.models import News
    return News.objects.create(
        title='Draft News',
        content='Draft Content',
        author=editor_user,
        status='DRAFT'
    )

@pytest.fixture
def editor_token(editor_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(editor_user)
    return str(refresh.access_token)

@pytest.fixture
def admin_token(admin_user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)

@pytest.fixture
def reader_token(reader_user):
    from rest_framework_simplejwt.tokens import RefreshToken
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