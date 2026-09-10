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
        instance = getattr(self, 'instance', None)
        start_time = attrs.get('start_time', getattr(instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(instance, 'end_time', None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': 'Giờ kết thúc phải sau giờ bắt đầu.'})

        return attrs
