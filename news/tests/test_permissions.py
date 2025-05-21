from django.test import TestCase, RequestFactory
from news.models import News
from users.permissions import IsEditorOrReadOnly, IsAdminOrReadOnly, IsOwnerOrReadOnly
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
        self.news = News.objects.create(
            title='Test News',
            content='Test Content',
            author=self.editor
        )

    def test_is_editor_or_read_only(self):
        permission = IsEditorOrReadOnly()
        
        # Test GET request (safe method)
        request = self.factory.get('/')
        request.user = self.reader
        self.assertTrue(permission.has_permission(request, None))
        
        # Test POST request as reader (should fail)
        request = self.factory.post('/')
        request.user = self.reader
        self.assertFalse(permission.has_permission(request, None))
        
        # Test POST request as editor (should pass)
        request = self.factory.post('/')
        request.user = self.editor
        self.assertTrue(permission.has_permission(request, None))

    def test_is_admin_or_read_only(self):
        permission = IsAdminOrReadOnly()
        
        # Test GET request (safe method)
        request = self.factory.get('/')
        request.user = self.reader
        self.assertTrue(permission.has_permission(request, None))
        
        # Test POST request as reader (should fail)
        request = self.factory.post('/')
        request.user = self.reader
        self.assertFalse(permission.has_permission(request, None))
        
        # Test POST request as admin (should pass)
        request = self.factory.post('/')
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))

    def test_is_owner_or_read_only(self):
        permission = IsOwnerOrReadOnly()

        # Test GET request (safe method)
        request = self.factory.get('/')
        request.user = self.reader
        self.assertTrue(permission.has_object_permission(request, None, self.news))

        # Test PUT request as non-owner (should fail)
        request = self.factory.put('/')
        request.user = self.reader