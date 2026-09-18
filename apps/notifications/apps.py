from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    label = 'notifications'

    def ready(self):
        # Import signals khi app khởi động để Django đăng ký các handler
        import apps.notifications.signals  # noqa
