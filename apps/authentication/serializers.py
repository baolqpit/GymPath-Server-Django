from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


# ══════════════════════════════════════════════════════════════════════════════
# Register
# ══════════════════════════════════════════════════════════════════════════════

class RegisterSerializer(serializers.ModelSerializer):
    """
    Nhận: username, password, password_confirm, email (optional), first_name, last_name
    Trả về: thông tin user vừa tạo (không có password)

    Validation cần implement:
    - password == password_confirm
    - username chưa tồn tại (ModelSerializer tự validate unique)
    - password đáp ứng AUTH_PASSWORD_VALIDATORS (dùng validate_password)
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name']
        read_only_fields = ['id']

    def validate(self, attrs):
        # TODO: Kiểm tra password == password_confirm
        # Nếu không khớp: raise serializers.ValidationError({"password_confirm": "..."})
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise serializers.ValidationError({'password_confirm': 'Mật khẩu xác nhận không khớp'})

        return attrs

    def create(self, validated_data):
        # TODO:
        # 1. Bỏ password_confirm ra khỏi validated_data
        # 2. Gọi User.objects.create_user(**validated_data) để hash password tự động
        # 3. Return user vừa tạo
        validated_data.pop("password_confirm", None)

        return User.objects.create_user(**validated_data)

# ══════════════════════════════════════════════════════════════════════════════
# Login – Custom token payload
# ══════════════════════════════════════════════════════════════════════════════

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Mở rộng payload của JWT để response trả thêm thông tin user.

    Flow:
    - validate() gọi super().validate() → nhận {'access': ..., 'refresh': ...}
    - Thêm user info vào response dict
    - Return dict đó

    TODO: Thêm các field muốn trả kèm token (username, email, full_name...)
    """

    def validate(self, attrs):
        # TODO:
        # 1. data = super().validate(attrs)  → có access + refresh token
        # 2. Lấy self.user (đã được set bởi parent)
        # 3. Gắn thêm: data['username'], data['email'], data['full_name']...
        # 4. return data
        data = super().validate(attrs)

        user = self.user
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name() or user.username,
        }

        return data

# ══════════════════════════════════════════════════════════════════════════════
# User Profile (GET /me và PATCH /me)
# ══════════════════════════════════════════════════════════════════════════════

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Dùng cho endpoint GET/PATCH /api/v1/auth/me/
    - GET: Trả về thông tin profile của user đang đăng nhập
    - PATCH: Cho phép cập nhật phone, date_of_birth, height_cm, weight_kg, bio,
             first_name, last_name (không cho đổi username/password ở đây)
    """

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'date_of_birth', 'height_cm', 'weight_kg', 'bio',
            'date_joined',
        ]
        read_only_fields = ['id', 'username', 'date_joined']


# ══════════════════════════════════════════════════════════════════════════════
# Change Password
# ══════════════════════════════════════════════════════════════════════════════

class ChangePasswordSerializer(serializers.Serializer):
    """
    Nhận: old_password, new_password, new_password_confirm

    Validation cần implement:
    - old_password phải đúng với password hiện tại của user
    - new_password == new_password_confirm
    - new_password đáp ứng AUTH_PASSWORD_VALIDATORS
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # TODO:
        # 1. Lấy user từ self.context['request'].user
        # 2. Kiểm tra user.check_password(attrs['old_password']) → sai thì raise error
        # 3. Kiểm tra new_password == new_password_confirm → sai thì raise error
        # 4. return attrs
        user = self.context['request'].userpublic
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'Mật khẩu hiện tại không chính xác.'})
        user.check_password(attrs['old_password'])

        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "Mật khẩu mới không trùng khớp"})

        return attrs