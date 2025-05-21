# subscriptions/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from datetime import timedelta
from users.permissions import IsSelfOrAdmin
from .models import SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer
from users.models import User


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Apenas admins podem gerenciar planos

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Endpoint para usuários se inscreverem em um plano"""
        plan = self.get_object()
        user = request.user

        # Verifica se já tem assinatura
        if hasattr(user, 'subscription'):
            return Response(
                {'detail': 'User already has an active subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cria a assinatura (30 dias de duração)
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            is_active=True
        )

        return Response(
            UserSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            return UserSubscription.objects.all()
        return UserSubscription.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_subscription(self, request):
        """Endpoint para o usuário ver sua própria assinatura"""
        if not hasattr(request.user, 'subscription'):
            return Response(
                {'detail': 'User has no subscription'},
                status=status.HTTP_404_NOT_FOUND
            )

        subscription = request.user.subscription
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def renew(self, request, pk=None):
        """Renova uma assinatura (apenas admin)"""
        subscription = self.get_object()
        subscription.end_date = subscription.end_date + timedelta(days=30)
        subscription.is_active = True
        subscription.save()
        return Response({'status': 'subscription renewed'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def cancel(self, request, pk=None):
        """Cancela uma assinatura (apenas admin)"""
        subscription = self.get_object()
        subscription.is_active = False
        subscription.save()
        return Response({'status': 'subscription canceled'})