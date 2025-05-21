from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription
from news.models import Category
from users.models import User
from django.utils import timezone
from datetime import timedelta


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    categories_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='categories',
        many=True,
        write_only=True,
        required=True
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'description',
            'price',
            'categories',
            'categories_ids',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='plan',
        write_only=True,
        required=True
    )
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False  # Não é obrigatório no create (pega do request.user)
    )
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'id',
            'user',
            'user_id',
            'plan',
            'plan_id',
            'start_date',
            'end_date',
            'is_active',
            'days_remaining',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['start_date', 'created_at', 'updated_at']

    def get_days_remaining(self, obj):
        if obj.end_date:
            remaining = (obj.end_date - timezone.now().date()).days
            return max(0, remaining)
        return None

    def validate(self, data):
        # Validação customizada para criação de assinatura
        if self.context['request'].method == 'POST':
            user = data.get('user', self.context['request'].user)

            # Verifica se usuário já tem assinatura ativa
            if UserSubscription.objects.filter(user=user, is_active=True).exists():
                raise serializers.ValidationError(
                    {"user": "User already has an active subscription"}
                )

            # Define datas padrão se não fornecidas
            if 'start_date' not in data:
                data['start_date'] = timezone.now().date()

            if 'end_date' not in data:
                data['end_date'] = data['start_date'] + timedelta(days=30)

            # Garante que a assinatura comece como ativa
            data['is_active'] = True

        return data


class SubscribeSerializer(serializers.Serializer):
    """
    Serializer específico para o endpoint de inscrição em planos
    """
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        required=True
    )
    payment_token = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Token do gateway de pagamento (opcional para testes)"
    )

    def create(self, validated_data):
        request = self.context['request']
        plan = validated_data['plan_id']

        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=plan,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True
        )

        # Aqui você implementaria a lógica de pagamento real
        if validated_data.get('payment_token'):
            # Processar pagamento com gateway (ex: Stripe, Pagar.me)
            pass

        return subscription


class RenewSubscriptionSerializer(serializers.Serializer):
    """
    Serializer para renovação de assinatura
    """
    months = serializers.IntegerField(
        min_value=1,
        max_value=12,
        default=1,
        help_text="Number of months to extend the subscription"
    )
    payment_token = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Token do gateway de pagamento"
    )

    def update(self, instance, validated_data):
        months = validated_data.get('months', 1)

        # Se a assinatura já expirou, renova a partir de hoje
        if instance.end_date < timezone.now().date():
            instance.start_date = timezone.now().date()
            instance.end_date = instance.start_date + timedelta(days=30 * months)
        else:
            # Caso contrário, estende a data final
            instance.end_date += timedelta(days=30 * months)

        instance.is_active = True
        instance.save()

        # Lógica de pagamento (simulada)
        if validated_data.get('payment_token'):
            # Processar pagamento
            pass

        return instance