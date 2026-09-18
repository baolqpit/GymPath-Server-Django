import logging

import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

from .models import DeviceToken

logger = logging.getLogger(__name__)


def _get_firebase_app():
    """
    Khởi tạo Firebase Admin SDK một lần duy nhất (singleton).

    Cần file service account JSON từ Firebase Console:
    Firebase Console → Project Settings → Service Accounts → Generate new private key
    → Lưu vào thư mục gốc dự án với tên 'firebase-service-account.json'
    → Thêm vào .gitignore
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()


class FCMService:
    """
    Service gửi push notification qua Firebase Cloud Messaging.

    Cách dùng:
        FCMService.send_to_user(user, title='Tiêu đề', body='Nội dung')
        FCMService.send_to_user(user, title='...', body='...', data={'key': 'value'})
    """

    @staticmethod
    def send_to_user(user, title: str, body: str, data: dict = None):
        """
        Gửi notification đến tất cả thiết bị active của user.

        Args:
            user: User instance
            title: Tiêu đề notification
            body: Nội dung notification
            data: Dict payload tuỳ chọn (gửi kèm data cho app xử lý)

        Flow:
        1. Lấy tất cả DeviceToken active của user
        2. Nếu không có token → bỏ qua
        3. Gọi _send_multicast() với danh sách tokens
        """
        # TODO:
        # tokens = DeviceToken.objects.filter(user=user, is_active=True).values_list('token', flat=True)
        # if not tokens:
        #     return
        # FCMService._send_multicast(list(tokens), title, body, data or {})
        tokens = DeviceToken.objects.filter(user=user, is_active=True).values_list('token', flat=True)

        if not tokens:
            return
        FCMService._send_multicast(tokens=list(tokens), title=title, body=body, data=data or {})

    @staticmethod
    def _send_multicast(tokens: list[str], title: str, body: str, data: dict):
        """
        Gửi multicast message đến danh sách tokens.

        Flow:
        1. Khởi tạo Firebase app
        2. Tạo MulticastMessage với notification + data
        3. Gọi messaging.send_each_for_multicast()
        4. Xử lý response: token nào fail (unregistered) → đánh dấu is_active=False
        """
        # TODO:
        # _get_firebase_app()
        #
        # message = messaging.MulticastMessage(
        #     tokens=tokens,
        #     notification=messaging.Notification(title=title, body=body),
        #     data={str(k): str(v) for k, v in data.items()},  # data chỉ nhận string
        # )
        #
        # response = messaging.send_each_for_multicast(message)
        #
        # # Xử lý token lỗi (thiết bị gỡ app / token hết hạn)
        # for idx, result in enumerate(response.responses):
        #     if not result.success:
        #         error_code = result.exception.code if result.exception else None
        #         if error_code in ('registration-token-not-registered', 'invalid-argument'):
        #             DeviceToken.objects.filter(token=tokens[idx]).update(is_active=False)
        #         logger.warning(f'FCM failed for token {tokens[idx][:20]}: {result.exception}')
        _get_firebase_app()

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data={str(key): str(value) for key, value in data.items()},
        )

        response = messaging.send_each_for_multicast(message)

        for idx, result in enumerate(response.responses):
            if not result.success:
                error_code = result.exception.code if result.exception else None
                if error_code in ('registration-token-not-registered', 'invalid-argument'):
                    DeviceToken.objects.filter(token=tokens[idx]).update(is_active=False)
                logger.warning(f'FCM failed for token {tokens[idx][:20]}: {result.exception}')

# ══════════════════════════════════════════════════════════════════════════════
# Các hàm notification cụ thể – gọi từ signals.py
# ══════════════════════════════════════════════════════════════════════════════

def notify_schedule_reminder(schedule):
    """
    #1 – Nhắc lịch tập sắp bắt đầu.
    Gọi từ scheduled task (Celery Beat / cron), không phải signal.

    Payload data cho app:
        type: 'schedule_reminder'
        schedule_id: '<id>'
    """
    # TODO:
    # FCMService.send_to_user(
    #     user=schedule.user,
    #     title='⏰ Sắp đến giờ tập!',
    #     body=f'{schedule.title} bắt đầu lúc {schedule.start_time.strftime("%H:%M")}',
    #     data={'type': 'schedule_reminder', 'schedule_id': str(schedule.id)},
    # )
    FCMService.send_to_user(
        user=schedule.user,
        title='⏰ Sắp đến giờ tập!',
        body=f'{schedule.title} bắt đầu lúc {schedule.start_time.strftime("%H:%M")}',
        data={
            'type': 'schedule_reminder',
            'schedule_id': str(schedule.id),
        }
    )


def notify_journal_prompt(schedule):
    """
    #2 – Nhắc ghi nhật ký sau khi đánh dấu hoàn thành lịch tập.
    Gọi từ signal post_save của TrainingSchedule khi is_completed đổi sang True.

    Payload data cho app:
        type: 'journal_prompt'
        schedule_id: '<id>'  → app tự điền title, date từ schedule này
    """
    # TODO:
    # FCMService.send_to_user(
    #     user=schedule.user,
    #     title='📝 Ghi lại buổi tập nào!',
    #     body=f'Bạn vừa hoàn thành "{schedule.title}". Ghi nhật ký để theo dõi tiến độ.',
    #     data={'type': 'journal_prompt', 'schedule_id': str(schedule.id)},
    # )
    FCMService.send_to_user(
        user=schedule.user,
        title='📝 Ghi lại buổi tập nào!',
        body=f'Bạn vừa hoàn thành "{schedule.title}". Ghi nhật ký để theo dõi tiến độ.',
        data={
            'type': 'journal_prompt',
            'schedule_id': str(schedule.id)
        }
    )


def notify_phase_completed(phase):
    """
    #3 – Thông báo hoàn thành giai đoạn lộ trình.
    Gọi từ signal post_save của RoadmapPhase khi is_completed đổi sang True.

    Payload data cho app:
        type: 'phase_completed'
        roadmap_id: '<id>'
        phase_id: '<id>'
    """
    # TODO:
    # FCMService.send_to_user(
    #     user=phase.roadmap.user,
    #     title='🏆 Hoàn thành giai đoạn!',
    #     body=f'Bạn đã hoàn thành "{phase.title}" trong lộ trình "{phase.roadmap.title}"!',
    #     data={
    #         'type': 'phase_completed',
    #         'roadmap_id': str(phase.roadmap.id),
    #         'phase_id': str(phase.id),
    #     },
    # )
    FCMService.send_to_user(
        user=phase.roadmap.user,
        title='🏆 Hoàn thành giai đoạn!',
        body=f'Bạn đã hoàn thành "{phase.title}" trong lộ trình "{phase.roadmap.title}"!',
        data={
            'type': 'phase_completed',
            'roadmap_id': str(phase.roadmap.id),
            'phase_id': str(phase.id)
        }
    )
