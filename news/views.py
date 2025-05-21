from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from jota_api import settings
from .models import News, Category
from .serializers import NewsSerializer, NewsCreateSerializer, CategorySerializer
from users.permissions import IsEditorOrReadOnly, IsAdminOrReadOnly, IsOwnerOrReadOnly
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .tasks import send_news_published_notification


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('-publication_date')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'access_level', 'categories', 'author']
    search_fields = ['title', 'subtitle', 'content']
    ordering_fields = ['publication_date', 'created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NewsCreateSerializer
        return NewsSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsEditorOrReadOnly]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Admins e Editores veem todas as notícias
        if self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'EDITOR']:
            return queryset
        
        # Para leitores (autenticados ou não), mostrar apenas notícias publicadas
        queryset = queryset.filter(status='PUBLISHED', publication_date__lte=timezone.now())
        
        # Verificar nível de acesso
        if self.request.user.is_authenticated and hasattr(self.request.user, 'subscription'):
            # Usuário autenticado com assinatura
            if self.request.user.subscription.plan.name == 'PRO':
                # Usuário PRO pode ver conteúdo PRO e FREE
                pass
            else:
                # Usuário com plano básico vê apenas conteúdo FREE
                queryset = queryset.filter(access_level='FREE')
            
            # Filtrar notícias pelas categorias do plano do usuário
            user_categories = self.request.user.subscription.plan.categories.all()
            queryset = queryset.filter(categories__in=user_categories).distinct()
        else:
            # Usuário não autenticado ou sem assinatura - apenas conteúdo FREE
            queryset = queryset.filter(access_level='FREE')
        
        return queryset

    def perform_create(self, serializer):
        news = serializer.save(author=self.request.user)
        if news.status == 'PUBLISHED' and settings.EMAIL_NOTIFICATION_ENABLED:
            send_news_published_notification.delay(news.id)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsEditorOrReadOnly])
    def publish(self, request, pk=None):
        news = self.get_object()
        news.status = 'PUBLISHED'
        if not news.publication_date:
            news.publication_date = timezone.now()
        news.save()
        return Response({'status': 'news published'}, status=status.HTTP_200_OK)