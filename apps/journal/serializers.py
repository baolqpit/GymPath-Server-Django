from django.db import transaction
from rest_framework import serializers

from .models import TrainingJournal, JournalExercise


class JournalExerciseSerializer(serializers.ModelSerializer):
    """
    Serializer cho từng bài tập trong nhật ký.

    Validate:
    - Ít nhất một trong sets/reps/duration_seconds phải có giá trị
    - weight_kg >= 0 nếu có
    """

    class Meta:
        model = JournalExercise
        fields = ['id', 'name', 'sets', 'reps', 'weight_kg', 'duration_seconds', 'notes']
        read_only_fields = ['id']

    def validate(self, attrs):
        # TODO:
        # 1. Kiểm tra: sets, reps, duration_seconds không phải tất cả đều None
        #    → Ít nhất phải có một thông tin để nhật ký có ý nghĩa
        # 2. Kiểm tra weight_kg >= 0 nếu có
        # 3. return attrs
        instance = getattr(self, 'instance', None)

        sets = attrs.get("sets", getattr(instance, "sets", None))
        reps = attrs.get("reps", getattr(instance, "reps", None))
        duration_seconds = attrs.get(
            "duration_seconds", getattr(instance, "duration_seconds", None)
        )
        weight_kg = attrs.get("weight_kg", getattr(instance, "weight_kg", None))

        if sets is None and reps is None and duration_seconds is None:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Bài tập cần ít nhất một thông tin về số set, số rep hoặc thời gian thực hiện (duration_seconds)."
                    ]
                }
            )

        if weight_kg is not None and weight_kg < 0:
            raise serializers.ValidationError(
                {"weight_kg": "Mức tạ (weight_kg) phải lớn hơn hoặc bằng 0."}
            )

        return attrs


class TrainingJournalSerializer(serializers.ModelSerializer):
    """
    Serializer cho nhật ký tập.

    - exercises: nested, hỗ trợ tạo/đọc exercises cùng lúc với journal
    - Khi tạo journal, có thể gửi kèm danh sách exercises trong body

    Ví dụ POST body:
        {
            "date": "2026-09-10",
            "title": "Tập ngực buổi sáng",
            "duration_minutes": 60,
            "mood": 4,
            "exercises": [
                {"name": "Bench Press", "sets": 4, "reps": 10, "weight_kg": 80},
                {"name": "Push Up", "sets": 3, "reps": 20}
            ]
        }
    """
    user = serializers.StringRelatedField(read_only=True)
    exercises = JournalExerciseSerializer(many=True, required=False)

    class Meta:
        model = TrainingJournal
        fields = [
            'id', 'user', 'date', 'title', 'notes',
            'duration_minutes', 'mood', 'calories_burned',
            'schedule', 'exercises',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # TODO:
        # 1. exercises_data = validated_data.pop('exercises', [])
        # 2. journal = TrainingJournal.objects.create(**validated_data)
        # 3. Với mỗi exercise_data trong exercises_data:
        #    JournalExercise.objects.create(journal=journal, **exercise_data)
        # 4. return journal
        exercises_data = validated_data.pop('exercises', [])

        with transaction.atomic():
            journal = TrainingJournal.objects.create(**validated_data)

            if exercises_data:
                exercise_instances = [
                    JournalExercise(journal=journal, **exercise_data)
                    for exercise_data in exercises_data
                ]
                JournalExercise.objects.bulk_create(exercise_instances)

        return journal

    def update(self, instance, validated_data):
        # TODO:
        # 1. exercises_data = validated_data.pop('exercises', None)
        # 2. Cập nhật các fields còn lại vào instance (dùng setattr + instance.save())
        # 3. Nếu exercises_data không phải None:
        #    → Xoá tất cả exercises cũ: instance.exercises.all().delete()
        #    → Tạo lại exercises mới từ exercises_data
        # 4. return instance
        exercises_data = validated_data.pop('exercises', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if exercises_data is not None:
                instance.exercises.all().delete()

            if exercises_data:
                new_exercises = [
                    JournalExercise(journal=instance, **item)
                    for item in exercises_data
                ]
                JournalExercise.objects.bulk_create(new_exercises)

        return instance

