from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.services import notify_schedule_reminder
from apps.schedule.models import TrainingSchedule


class Command(BaseCommand):
    help = 'Gửi FCM nhắc lịch tập sắp bắt đầu. Chạy bằng cron mỗi 5–15 phút.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Nhắc trước bao nhiêu phút so với start_time (mặc định: 30)',
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        now = timezone.localtime()
        window_start = now.time()
        window_end = (now + timedelta(minutes=minutes)).time()

        # Lấy các lịch tập trong ngày hôm nay, chưa hoàn thành,
        # có start_time nằm trong khoảng [bây giờ, bây giờ + N phút]
        schedules = TrainingSchedule.objects.filter(
            date=now.date(),
            is_completed=False,
            start_time__gte=window_start,
            start_time__lte=window_end,
        ).select_related('user')

        count = 0
        for schedule in schedules:
            try:
                notify_schedule_reminder(schedule)
                count += 1
            except Exception as e:
                self.stderr.write(
                    f'[ERROR] schedule_id={schedule.pk} user_id={schedule.user_id}: {e}'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'[{now.strftime("%H:%M")}] Đã gửi {count} reminder(s) '
                f'(window: {minutes} phút tới).'
            )
        )
