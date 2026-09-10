from rest_framework import serializers

from .models import TrainingSchedule


class TrainingScheduleSerializer(serializers.ModelSerializer):
    """
    Dùng cho tất cả CRUD của lịch tập.

    - user: read-only, tự gán từ request.user trong view (không để client tự set)
    - Validate:
        * end_time phải sau start_time nếu cả hai đều có
        * date không được là ngày trong quá khứ khi tạo mới (optional – tùy business)
    """
    user = serializers.StringRelatedField(read_only=True)  # Hiển thị username

    class Meta:
        model = TrainingSchedule
        fields = [
            'id', 'user', 'title', 'description',
            'date', 'start_time', 'end_time',
            'difficulty', 'is_completed', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        # TODO:
        # 1. Lấy start_time và end_time từ attrs
        # 2. Nếu cả hai đều có: kiểm tra end_time > start_time
        #    → Sai thì raise serializers.ValidationError({"end_time": "..."})
        # 3. return attrs
        raise NotImplementedError
