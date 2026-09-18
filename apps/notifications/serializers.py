from rest_framework import serializers
from .models import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    """
    Dùng cho POST /api/v1/notifications/device-token/ (đăng ký token mới)
    và DELETE /api/v1/notifications/device-token/ (huỷ đăng ký khi logout).

    token: FCM registration token lấy từ Firebase SDK phía app.
    platform: 'android' hoặc 'ios'.
    """

    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """
        Upsert token: nếu token đã tồn tại thì cập nhật user + is_active=True,
        tránh duplicate khi app gọi lại sau khi token refresh.

        TODO:
        1. user = self.context['request'].user
        2. token, _ = DeviceToken.objects.update_or_create(
               token=validated_data['token'],
               defaults={'user': user, 'platform': validated_data['platform'], 'is_active': True}
           )
        3. return token
        """
        user = self.context['request'].user
        token, _ = DeviceToken.objects.update_or_create(
            token=validated_data['token'],
            defaults={'user': user, 'platform': validated_data['platform'], 'is_active': True}
        )
        return token
