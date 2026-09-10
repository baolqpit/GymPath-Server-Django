from django.conf import settings
from django.db import models


class TrainingJournal(models.Model):
    """
    Nhật ký ghi lại buổi tập đã thực hiện.

    Khác với Schedule (kế hoạch tương lai),
    Journal là bản ghi thực tế sau khi tập xong.
    Có thể liên kết với Schedule nếu muốn theo dõi thực vs kế hoạch.
    """
    MOOD_CHOICES = [
        (1, 'Rất tệ'),
        (2, 'Tệ'),
        (3, 'Bình thường'),
        (4, 'Tốt'),
        (5, 'Tuyệt vời'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='journals',
    )
    date = models.DateField(help_text='Ngày tập thực tế')
    title = models.CharField(max_length=200, help_text='Tên buổi tập')
    notes = models.TextField(blank=True, null=True, help_text='Cảm nhận, ghi chú sau buổi tập')
    duration_minutes = models.PositiveIntegerField(
        blank=True, null=True, help_text='Thời lượng tập (phút)'
    )
    mood = models.IntegerField(
        choices=MOOD_CHOICES, blank=True, null=True,
        help_text='Cảm giác sau buổi tập (1-5)'
    )
    calories_burned = models.PositiveIntegerField(
        blank=True, null=True, help_text='Calo đốt cháy (ước tính)'
    )
    # Liên kết với lịch tập nếu muốn (optional)
    schedule = models.OneToOneField(
        'schedule.TrainingSchedule',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='journal',
        help_text='Lịch tập tương ứng (nếu có)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_journals'
        ordering = ['-date', '-created_at']
        verbose_name = 'Nhật ký tập'
        verbose_name_plural = 'Nhật ký tập'

    def __str__(self):
        return f'{self.user.username} – {self.title} ({self.date})'


class JournalExercise(models.Model):
    """
    Chi tiết từng bài tập trong một buổi nhật ký.

    Ví dụ: Journal "Tập ngực 10/09" → Bench Press: 4 sets x 10 reps x 80kg
    """
    journal = models.ForeignKey(
        TrainingJournal,
        on_delete=models.CASCADE,
        related_name='exercises',
    )
    name = models.CharField(max_length=200, help_text='Tên bài tập')
    sets = models.PositiveIntegerField(blank=True, null=True, help_text='Số set')
    reps = models.PositiveIntegerField(blank=True, null=True, help_text='Số rep mỗi set')
    weight_kg = models.FloatField(blank=True, null=True, help_text='Tạ (kg)')
    duration_seconds = models.PositiveIntegerField(
        blank=True, null=True, help_text='Thời gian (giây) – dùng cho cardio/plank'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'journal_exercises'
        verbose_name = 'Bài tập trong nhật ký'
        verbose_name_plural = 'Bài tập trong nhật ký'

    def __str__(self):
        return f'{self.name} – {self.journal}'
