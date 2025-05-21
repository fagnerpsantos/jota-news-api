from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('EDITOR', 'Editor'),
        ('READER', 'Leitor'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='READER')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_editor(self):
        return self.role == 'EDITOR'

    @property
    def is_reader(self):
        return self.role == 'READER'