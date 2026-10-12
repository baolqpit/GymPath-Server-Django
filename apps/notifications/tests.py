from datetime import date, time
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import User
from apps.notifications.models import DeviceToken
from apps.roadmap.models import Roadmap, RoadmapPhase
from apps.schedule.models import TrainingSchedule


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_user(username='testuser', password='Pass123!'):
    return User.objects.create_user(username=username, password=password)


def auth_client(user):
    """Trả về APIClient đã gắn JWT Bearer token."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


# ─────────────────────────────────────────────────────────────────────────────
# 1. Device Token API
# ─────────────────────────────────────────────────────────────────────────────

class DeviceTokenAPITest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)
        self.url = reverse('device-token')

    def test_register_token_returns_201(self):
        res = self.client.post(self.url, {
            'token': 'fcm-token-abc123',
            'platform': 'android',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['token'], 'fcm-token-abc123')
        self.assertTrue(DeviceToken.objects.filter(token='fcm-token-abc123').exists())

    def test_register_token_upsert_reactivates(self):
        """Token đã tồn tại + is_active=False → POST phải set is_active=True lại."""
        DeviceToken.objects.create(user=self.user, token='fcm-token-xyz', is_active=False)

        self.client.post(self.url, {'token': 'fcm-token-xyz', 'platform': 'android'})

        token = DeviceToken.objects.get(token='fcm-token-xyz')
        self.assertTrue(token.is_active)

    def test_register_token_upsert_no_duplicate(self):
        """Gọi POST hai lần với cùng token → vẫn chỉ có 1 record."""
        self.client.post(self.url, {'token': 'fcm-dup', 'platform': 'android'})
        self.client.post(self.url, {'token': 'fcm-dup', 'platform': 'ios'})

        self.assertEqual(DeviceToken.objects.filter(token='fcm-dup').count(), 1)

    def test_deactivate_token_returns_204(self):
        DeviceToken.objects.create(user=self.user, token='fcm-del-token')

        res = self.client.delete(self.url, {'token': 'fcm-del-token'})

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DeviceToken.objects.get(token='fcm-del-token').is_active)

    def test_deactivate_without_token_returns_400(self):
        res = self.client.delete(self.url, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        res = APIClient().post(self.url, {'token': 'x', 'platform': 'android'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FCMService (mock Firebase)
# ─────────────────────────────────────────────────────────────────────────────

class FCMServiceTest(TestCase):

    def setUp(self):
        self.user = make_user('fcmuser')

    @patch('apps.notifications.services._get_firebase_app')
    @patch('apps.notifications.services.messaging')
    def test_send_to_user_calls_multicast(self, mock_messaging, mock_app):
        DeviceToken.objects.create(user=self.user, token='valid-token', is_active=True)

        mock_response = MagicMock()
        mock_response.responses = [MagicMock(success=True)]
        mock_messaging.send_each_for_multicast.return_value = mock_response

        from apps.notifications.services import FCMService
        FCMService.send_to_user(self.user, title='Test', body='Body')

        mock_messaging.send_each_for_multicast.assert_called_once()

    @patch('apps.notifications.services._get_firebase_app')
    @patch('apps.notifications.services.messaging')
    def test_send_to_user_skips_if_no_tokens(self, mock_messaging, mock_app):
        """Không có token → không gọi Firebase."""
        from apps.notifications.services import FCMService
        FCMService.send_to_user(self.user, title='Test', body='Body')

        mock_messaging.send_each_for_multicast.assert_not_called()

    @patch('apps.notifications.services._get_firebase_app')
    @patch('apps.notifications.services.messaging')
    def test_failed_token_deactivated(self, mock_messaging, mock_app):
        """Token bị Firebase báo lỗi → is_active=False."""
        DeviceToken.objects.create(user=self.user, token='bad-token', is_active=True)

        failed = MagicMock(success=False)
        failed.exception.code = 'registration-token-not-registered'
        mock_response = MagicMock()
        mock_response.responses = [failed]
        mock_messaging.send_each_for_multicast.return_value = mock_response

        from apps.notifications.services import FCMService
        FCMService.send_to_user(self.user, title='Test', body='Body')

        self.assertFalse(DeviceToken.objects.get(token='bad-token').is_active)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Signal: on_schedule_completed
# ─────────────────────────────────────────────────────────────────────────────

class ScheduleCompletedSignalTest(TestCase):

    def setUp(self):
        self.user = make_user('signaluser')
        self.schedule = TrainingSchedule.objects.create(
            user=self.user,
            title='Buổi tập ngực',
            date=date.today(),
            is_completed=False,
        )

    @patch('apps.notifications.signals.notify_journal_prompt')
    def test_signal_fires_when_completed_changes_to_true(self, mock_notify):
        self.schedule.is_completed = True
        self.schedule.save()

        mock_notify.assert_called_once_with(self.schedule)

    @patch('apps.notifications.signals.notify_journal_prompt')
    def test_signal_does_not_fire_on_create(self, mock_notify):
        TrainingSchedule.objects.create(
            user=self.user,
            title='Buổi mới',
            date=date.today(),
            is_completed=True,   # Tạo mới với is_completed=True luôn → không bắn
        )
        mock_notify.assert_not_called()

    @patch('apps.notifications.signals.notify_journal_prompt')
    def test_signal_does_not_fire_when_already_completed(self, mock_notify):
        """Đã completed rồi, save lần nữa → không bắn thêm."""
        self.schedule.is_completed = True
        self.schedule.save()
        mock_notify.reset_mock()

        self.schedule.title = 'Đổi tên'
        self.schedule.save()

        mock_notify.assert_not_called()

    @patch('apps.notifications.signals.notify_journal_prompt')
    def test_signal_does_not_fire_when_still_incomplete(self, mock_notify):
        self.schedule.notes = 'Ghi chú thêm'
        self.schedule.save()

        mock_notify.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# 4. Signal: on_phase_completed
# ─────────────────────────────────────────────────────────────────────────────

class PhaseCompletedSignalTest(TestCase):

    def setUp(self):
        self.user = make_user('phaseuser')
        self.roadmap = Roadmap.objects.create(
            user=self.user,
            title='Lộ trình test',
            goal='general',
            start_date=date.today(),
        )
        self.phase = RoadmapPhase.objects.create(
            roadmap=self.roadmap,
            title='Phase 1',
            order=1,
            is_completed=False,
        )

    @patch('apps.notifications.signals.notify_phase_completed')
    def test_signal_fires_when_phase_completed(self, mock_notify):
        self.phase.is_completed = True
        self.phase.save()

        mock_notify.assert_called_once_with(self.phase)

    @patch('apps.notifications.signals.notify_phase_completed')
    def test_signal_does_not_fire_on_create(self, mock_notify):
        RoadmapPhase.objects.create(
            roadmap=self.roadmap,
            title='Phase 2',
            order=2,
            is_completed=True,
        )
        mock_notify.assert_not_called()

    @patch('apps.notifications.signals.notify_phase_completed')
    def test_signal_does_not_fire_when_already_completed(self, mock_notify):
        self.phase.is_completed = True
        self.phase.save()
        mock_notify.reset_mock()

        self.phase.title = 'Đổi tên phase'
        self.phase.save()

        mock_notify.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Management command: send_schedule_reminders
# ─────────────────────────────────────────────────────────────────────────────

class SendScheduleRemindersCommandTest(TestCase):

    def setUp(self):
        from django.utils import timezone
        self.user = make_user('cronuser')
        self.now = timezone.localtime()

    @patch('apps.notifications.management.commands.send_schedule_reminders.notify_schedule_reminder')
    def test_command_sends_reminder_for_upcoming_schedule(self, mock_notify):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone

        now = timezone.localtime()
        upcoming_time = (now + timedelta(minutes=20)).time()

        TrainingSchedule.objects.create(
            user=self.user,
            title='Buổi sắp tới',
            date=now.date(),
            start_time=upcoming_time,
            is_completed=False,
        )

        call_command('send_schedule_reminders', minutes=30)

        mock_notify.assert_called_once()

    @patch('apps.notifications.management.commands.send_schedule_reminders.notify_schedule_reminder')
    def test_command_skips_completed_schedule(self, mock_notify):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone

        now = timezone.localtime()
        upcoming_time = (now + timedelta(minutes=20)).time()

        TrainingSchedule.objects.create(
            user=self.user,
            title='Đã hoàn thành rồi',
            date=now.date(),
            start_time=upcoming_time,
            is_completed=True,   # Đã xong → không nhắc
        )

        call_command('send_schedule_reminders', minutes=30)

        mock_notify.assert_not_called()

    @patch('apps.notifications.management.commands.send_schedule_reminders.notify_schedule_reminder')
    def test_command_skips_schedule_outside_window(self, mock_notify):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone

        now = timezone.localtime()
        far_time = (now + timedelta(hours=3)).time()

        TrainingSchedule.objects.create(
            user=self.user,
            title='Buổi tập xa',
            date=now.date(),
            start_time=far_time,
            is_completed=False,
        )

        call_command('send_schedule_reminders', minutes=30)  # window chỉ 30 phút

        mock_notify.assert_not_called()
