from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    VERTICAL_CHOICES = [
        ('PODER', 'Poder'),
        ('TRIBUTOS', 'Tributos'),
        ('SAUDE', 'Saúde'),
        ('ENERGIA', 'Energia'),
        ('TRABALHISTA', 'Trabalhista'),
    ]

    name = models.CharField(max_length=50, choices=VERTICAL_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class News(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('PUBLISHED', 'Publicada'),
    ]

    ACCESS_CHOICES = [
        ('FREE', 'Todos os leitores'),
        ('PRO', 'Clientes PRO'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    content = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='FREE')
    categories = models.ManyToManyField(Category, related_name='news')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-publication_date']