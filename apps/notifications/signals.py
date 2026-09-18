from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.roadmap.models import RoadmapPhase
from apps.schedule.models import TrainingSchedule
from .services import notify_journal_prompt, notify_phase_completed


# ══════════════════════════════════════════════════════════════════════════════
# Signal #2: Nhắc ghi nhật ký khi đánh dấu lịch tập hoàn thành
# ══════════════════════════════════════════════════════════════════════════════

@receiver(pre_save, sender=TrainingSchedule)
def _cache_schedule_is_completed(sender, instance, **kwargs):
    """
    Chạy TRƯỚC khi lưu DB. Lưu giá trị is_completed hiện tại vào thuộc tính
    tạm trên instance để post_save có thể so sánh "trước và sau".

    Nếu là record mới (chưa có pk) → gán False làm giá trị mặc định.
    """
    if instance.pk:
        old = TrainingSchedule.objects.filter(pk=instance.pk).values('is_completed').first()
        instance.__original_is_completed = old['is_completed'] if old else False
    else:
        instance.__original_is_completed = False


@receiver(post_save, sender=TrainingSchedule)
def on_schedule_completed(sender, instance, created, **kwargs):
    """
    Chạy SAU khi lưu DB. Bắn notification nhắc ghi nhật ký khi
    is_completed vừa được đổi từ False → True (chỉ bắn đúng 1 lần).
    """
    if created:
        return

    was_completed = getattr(instance, '__original_is_completed', False)
    if not was_completed and instance.is_completed:
        notify_journal_prompt(instance)


# ══════════════════════════════════════════════════════════════════════════════
# Signal #3: Thông báo hoàn thành giai đoạn lộ trình
# ══════════════════════════════════════════════════════════════════════════════

@receiver(pre_save, sender=RoadmapPhase)
def _cache_phase_is_completed(sender, instance, **kwargs):
    """Lưu giá trị is_completed cũ trước khi lưu DB."""
    if instance.pk:
        old = RoadmapPhase.objects.filter(pk=instance.pk).values('is_completed').first()
        instance.__original_is_completed = old['is_completed'] if old else False
    else:
        instance.__original_is_completed = False


@receiver(post_save, sender=RoadmapPhase)
def on_phase_completed(sender, instance, created, **kwargs):
    """
    Bắn notification khi is_completed vừa đổi từ False → True.
    """
    if created:
        return

    was_completed = getattr(instance, '__original_is_completed', False)
    if not was_completed and instance.is_completed:
        notify_phase_completed(instance)
