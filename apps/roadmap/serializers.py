from rest_framework import serializers

from .models import Roadmap, RoadmapPhase


class RoadmapPhaseSerializer(serializers.ModelSerializer):
    """
    Serializer cho một giai đoạn (phase) của lộ trình.

    Validate:
    - end_date >= start_date nếu cả hai có
    - order phải >= 1
    """

    class Meta:
        model = RoadmapPhase
        fields = [
            'id', 'title', 'description', 'order',
            'start_date', 'end_date', 'is_completed',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # TODO:
        # 1. Nếu start_date và end_date đều có: kiểm tra end_date >= start_date
        # 2. return attrs
        instance = getattr(self, 'isntance', None)

        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))

        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'Ngày kết thúc phải sau ngày bắt đầu.'
            })

        return attrs


class RoadmapSerializer(serializers.ModelSerializer):
    """
    Serializer cho lộ trình.

    - phases: nested read-only, hiển thị tất cả phases khi GET
    - Khi tạo/sửa roadmap, dùng endpoint riêng cho phases (xem urls.py)

    Validate:
    - end_date >= start_date nếu end_date có
    """
    user = serializers.StringRelatedField(read_only=True)
    phases = RoadmapPhaseSerializer(many=True, read_only=True)

    class Meta:
        model = Roadmap
        fields = [
            'id', 'user', 'title', 'description', 'goal',
            'start_date', 'end_date', 'is_active',
            'phases', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        # TODO:
        # 1. Nếu end_date có: kiểm tra end_date > start_date
        # 2. return attrs
        instance = getattr(self, 'instance', None)

        end_date = attrs.get('end_date', getattr(instance, 'end_date', None))
        start_date = attrs.get('start_date', getattr(instance, 'start_date', None))

        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'Ngày kết thúc phải sau ngày bắt đầu.'
            })

        return attrs
