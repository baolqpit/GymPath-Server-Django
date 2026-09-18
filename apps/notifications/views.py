from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import serializers

from .models import DeviceToken
from .serializers import DeviceTokenSerializer


class DeviceTokenView(APIView):
    """
    POST   /api/v1/notifications/device-token/  → Đăng ký FCM token (gọi khi app khởi động / token refresh)
    DELETE /api/v1/notifications/device-token/  → Huỷ token (gọi khi user logout)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Notifications'],
        summary='Đăng ký FCM device token',
        request=DeviceTokenSerializer,
        responses={201: DeviceTokenSerializer},
    )
    def post(self, request):
        """
        App gọi endpoint này sau khi lấy được FCM token từ Firebase SDK.

        Flow:
        1. serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
        2. serializer.is_valid(raise_exception=True)
        3. serializer.save()
        4. return Response(serializer.data, status=201)

        Request body: { "token": "<fcm_token>", "platform": "android" }
        """
        # TODO: Implement
        serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Notifications'],
        summary='Huỷ FCM device token khi logout',
        request={'application/json': {'type': 'object', 'properties': {
            'token': {'type': 'string'}
        }, 'required': ['token']}},
        responses={204: None},
    )
    def delete(self, request):
        """
        App gọi endpoint này khi user logout để không nhận notification nữa.

        Flow:
        1. token = request.data.get('token')
        2. Nếu không có → return 400
        3. DeviceToken.objects.filter(user=request.user, token=token).update(is_active=False)
        4. return Response(status=204)
        """
        # TODO: Implement
        token = request.data.get('token')

        if not token:
            raise serializers.ValidationError({
                "token": "Device token is required."
            })

        DeviceToken.objects.filter(user=request.user, token=token).update(is_active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)
