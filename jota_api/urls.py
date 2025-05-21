from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from news.views import NewsViewSet, CategoryViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="JOTA News API",
        default_version='v1',
        description="API para o sistema de notícias da JOTA",
        terms_of_service="https://www.jota.com/terms/",
        contact=openapi.Contact(email="contato@jota.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
