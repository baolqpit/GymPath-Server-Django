from django.conf import settings
from django.db import models


class TrainingSchedule(models.Model):
    """
    Lịch tập của một user trong một ngày cụ thể.

    Ví dụ: "Ngày 10/09 – Buổi tập ngực + tay", bắt đầu 06:00, kết thúc 07:30.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Nhẹ'),
        ('medium', 'Vừa'),
        ('hard', 'Nặng'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    title = models.CharField(max_length=200, help_text='Tên buổi tập')
    description = models.TextField(blank=True, null=True, help_text='Mô tả chi tiết buổi tập')
    date = models.DateField(help_text='Ngày tập')
    start_time = models.TimeField(blank=True, null=True, help_text='Giờ bắt đầu')
    end_time = models.TimeField(blank=True, null=True, help_text='Giờ kết thúc')
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_CHOICES, default='medium'
    )
    is_completed = models.BooleanField(default=False, help_text='Đã hoàn thành chưa')
    notes = models.TextField(blank=True, null=True, help_text='Ghi chú thêm')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_schedules'
        ordering = ['date', 'start_time']
        verbose_name = 'Lịch tập'
        verbose_name_plural = 'Lịch tập'

    def __str__(self):
        return f'{self.user.username} – {self.title} ({self.date})'
