from tokenize import TokenError

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/register/
# ══════════════════════════════════════════════════════════════════════════════

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Đăng ký tài khoản',
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
    )
    def post(self, request):
        # TODO:
        # 1. serializer = RegisterSerializer(data=request.data)
        # 2. serializer.is_valid(raise_exception=True)
        #    → Nếu invalid, DRF tự return 400 với error detail
        # 3. user = serializer.save()
        # 4. Return Response(RegisterSerializer(user).data, status=201)
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(RegisterSerializer(user).data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/login/
# ══════════════════════════════════════════════════════════════════════════════

@extend_schema(tags=['Auth'], summary='Đăng nhập – nhận access & refresh token')
class LoginView(TokenObtainPairView):
    """
    Đăng nhập bằng username + password. Trả về access & refresh token.

    Request body:
        { "username": "john", "password": "StrongPass123!" }

    Response 200:
        {
            "access": "<JWT access token>",
            "refresh": "<JWT refresh token>",
            "username": "john",
            "email": "john@example.com"
        }

    Response 401:
        { "detail": "No active account found with the given credentials" }
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer  # Dùng custom để thêm user info


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/refresh/
# ══════════════════════════════════════════════════════════════════════════════
# Dùng trực tiếp TokenRefreshView của simplejwt (đăng ký trong urls.py).
# Request body: { "refresh": "<refresh token>" }
# Response 200: { "access": "<new access token>", "refresh": "<new refresh token>" }


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/logout/
# ══════════════════════════════════════════════════════════════════════════════

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Đăng xuất – blacklist refresh token',
        request={'application/json': {'type': 'object', 'properties': {
            'refresh': {'type': 'string', 'description': 'Refresh token cần vô hiệu hóa'}
        }, 'required': ['refresh']}},
        responses={204: None, 400: {"description": "Refresh token không hợp lệ hoặc thiếu"}},
    )
    def post(self, request):
        # TODO:
        # 1. refresh_token = request.data.get('refresh')
        # 2. Nếu không có → return 400
        # 3. token = RefreshToken(refresh_token)
        # 4. token.blacklist()
        # 5. return Response(status=204)
        # Bọc trong try/except TokenError → return 400 nếu token invalid
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"detail": "Refresh token là bắt buộc."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

# ══════════════════════════════════════════════════════════════════════════════
# GET/PATCH /api/v1/auth/me/
# ══════════════════════════════════════════════════════════════════════════════

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Lấy thông tin profile của user hiện tại',
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        # TODO:
        # 1. serializer = UserProfileSerializer(request.user)
        # 2. return Response(serializer.data)
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=['Auth'],
        summary='Cập nhật profile (partial)',
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
    )
    def patch(self, request):
        # TODO:
        # 1. serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        # 2. serializer.is_valid(raise_exception=True)
        # 3. serializer.save()
        # 4. return Response(serializer.data)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# ══════════════════════════════════════════════════════════════════════════════
# POST /api/v1/auth/change-password/
# ══════════════════════════════════════════════════════════════════════════════

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Đổi mật khẩu',
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description='Đổi mật khẩu thành công.')},
    )
    def post(self, request):
        # TODO:
        # 1. serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        # 2. serializer.is_valid(raise_exception=True)
        # 3. user = request.user
        # 4. user.set_password(serializer.validated_data['new_password'])
        # 5. user.save()
        # 6. return Response({"detail": "Đổi mật khẩu thành công."})
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Đổi mật khẩu thành công"})