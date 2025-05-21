from django.db import models
from django.conf import settings
from news.models import Category


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('INFO', 'JOTA Info'),
        ('PRO', 'JOTA PRO'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category, related_name='subscription_plans')

    def __str__(self):
        return self.get_name_display()


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    class Meta:
        ordering = ['-end_date']