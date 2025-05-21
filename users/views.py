from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserSubscriptionSerializer
from .permissions import IsSelfOrAdmin
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = []
        elif self.action == 'register':
            permission_classes = []
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def subscription(self, request, pk=None):
        user = self.get_object()
        if request.method == 'POST':
            serializer = UserSubscriptionSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if hasattr(user, 'subscription'):
            serializer = UserSubscriptionSerializer(user.subscription)
            return Response(serializer.data)
        return Response({'detail': 'No subscription found'}, status=status.HTTP_404_NOT_FOUND)