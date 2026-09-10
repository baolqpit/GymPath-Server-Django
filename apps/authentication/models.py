from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model mở rộng từ AbstractUser.
    Kế thừa sẵn: username, email, password, first_name, last_name, is_active, date_joined...

    Thêm các field bổ sung cho GymPath:
    """
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height_cm = models.FloatField(blank=True, null=True, help_text='Chiều cao (cm)')
    weight_kg = models.FloatField(blank=True, null=True, help_text='Cân nặng (kg)')
    bio = models.TextField(blank=True, null=True, help_text='Giới thiệu bản thân')

    class Meta:
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return self.username
