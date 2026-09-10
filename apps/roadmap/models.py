from django.conf import settings
from django.db import models


class Roadmap(models.Model):
    """
    Lộ trình tập luyện tổng thể của user.

    Ví dụ: "Giảm 10kg trong 3 tháng", "Tăng cơ mùa đông 2026".
    Một lộ trình có nhiều Phase (giai đoạn).
    """
    GOAL_CHOICES = [
        ('weight_loss', 'Giảm cân'),
        ('muscle_gain', 'Tăng cơ'),
        ('endurance', 'Tăng sức bền'),
        ('flexibility', 'Tăng linh hoạt'),
        ('general', 'Tổng quát'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text='Đang thực hiện hay không')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmaps'
        ordering = ['-created_at']
        verbose_name = 'Lộ trình'
        verbose_name_plural = 'Lộ trình'

    def __str__(self):
        return f'{self.user.username} – {self.title}'


class RoadmapPhase(models.Model):
    """
    Giai đoạn trong lộ trình.

    Ví dụ: Roadmap "Giảm 10kg" → Phase 1 "Quen vận động" (tuần 1-4),
                                   Phase 2 "Tăng cường độ" (tuần 5-8),
                                   Phase 3 "Duy trì" (tuần 9-12).
    """
    roadmap = models.ForeignKey(
        Roadmap,
        on_delete=models.CASCADE,
        related_name='phases',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1, help_text='Thứ tự giai đoạn')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'roadmap_phases'
        ordering = ['order']
        verbose_name = 'Giai đoạn lộ trình'
        verbose_name_plural = 'Giai đoạn lộ trình'

    def __str__(self):
        return f'[Phase {self.order}] {self.title} – {self.roadmap.title}'
