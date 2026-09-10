from datetime import date, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.journal.models import JournalExercise, TrainingJournal
from apps.roadmap.models import Roadmap, RoadmapPhase
from apps.schedule.models import TrainingSchedule

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed dữ liệu mẫu cho user có id=1'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(pk=1)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Không tìm thấy user có id=1. Hãy tạo superuser trước.'))
            return

        with transaction.atomic():
            self._seed_schedules(user)
            self._seed_roadmaps(user)
            self._seed_journals(user)

        self.stdout.write(self.style.SUCCESS(f'Seed data thành công cho user: {user.username}'))

    # ──────────────────────────────────────────────────────────────────────────
    # SCHEDULE
    # ──────────────────────────────────────────────────────────────────────────
    def _seed_schedules(self, user):
        schedules = [
            # Đã hoàn thành (quá khứ)
            dict(title='Ngực + Vai', date=date(2026, 9, 1), start_time=time(6, 0), end_time=time(7, 30),
                 difficulty='medium', is_completed=True,
                 description='Bench press, Shoulder press, Lateral raise',
                 notes='Cảm giác tốt, tăng được 2.5kg so với tuần trước'),

            dict(title='Lưng + Tay sau', date=date(2026, 9, 3), start_time=time(6, 0), end_time=time(7, 30),
                 difficulty='hard', is_completed=True,
                 description='Deadlift, Pull-up, Barbell row, Tricep pushdown',
                 notes='Deadlift PR mới: 120kg x 5'),

            dict(title='Chân', date=date(2026, 9, 5), start_time=time(6, 30), end_time=time(8, 0),
                 difficulty='hard', is_completed=True,
                 description='Squat, Leg press, Romanian deadlift, Leg curl',
                 notes='Đau đùi sau nhưng squat form đã cải thiện'),

            dict(title='Cardio + Core', date=date(2026, 9, 7), start_time=time(7, 0), end_time=time(8, 0),
                 difficulty='easy', is_completed=True,
                 description='Chạy 5km + Plank + Crunches',
                 notes='Chạy 5km trong 28 phút'),

            dict(title='Ngực + Tay trước', date=date(2026, 9, 9), start_time=time(6, 0), end_time=time(7, 30),
                 difficulty='medium', is_completed=True,
                 description='Incline bench, Cable fly, Barbell curl, Hammer curl'),

            # Hôm nay
            dict(title='Lưng + Tay sau', date=date(2026, 9, 10), start_time=time(6, 0), end_time=time(7, 30),
                 difficulty='hard', is_completed=False,
                 description='Deadlift 4x5, Pull-up 4x8, Barbell row 4x10, Face pull 3x15'),

            # Tương lai
            dict(title='Chân', date=date(2026, 9, 12), start_time=time(6, 30), end_time=time(8, 0),
                 difficulty='hard', is_completed=False,
                 description='Squat 4x6, Leg press 4x12, RDL 3x10, Leg curl 3x12'),

            dict(title='Vai + Cardio', date=date(2026, 9, 14), start_time=time(7, 0), end_time=time(8, 30),
                 difficulty='medium', is_completed=False,
                 description='OHP 4x8, Lateral raise 4x15, Chạy 20 phút'),
        ]

        for data in schedules:
            TrainingSchedule.objects.get_or_create(
                user=user, title=data['title'], date=data['date'],
                defaults=data,
            )

        self.stdout.write(f'  ✓ {len(schedules)} schedules')

    # ──────────────────────────────────────────────────────────────────────────
    # ROADMAP
    # ──────────────────────────────────────────────────────────────────────────
    def _seed_roadmaps(self, user):
        # Roadmap 1: Tăng cơ (đang thực hiện)
        roadmap1, _ = Roadmap.objects.get_or_create(
            user=user, title='Tăng cơ mùa thu 2026',
            defaults=dict(
                description='Mục tiêu tăng 3kg cơ trong 12 tuần, tập 4 buổi/tuần theo giáo án Upper-Lower.',
                goal='muscle_gain',
                start_date=date(2026, 9, 1),
                end_date=date(2026, 11, 24),
                is_active=True,
            )
        )

        phases1 = [
            dict(order=1, title='Giai đoạn 1 – Làm quen', is_completed=True,
                 start_date=date(2026, 9, 1), end_date=date(2026, 9, 21),
                 description='Tập quen giáo án, chú trọng form. Tăng dần trọng lượng 2.5kg/tuần.'),
            dict(order=2, title='Giai đoạn 2 – Tăng cường độ', is_completed=False,
                 start_date=date(2026, 9, 22), end_date=date(2026, 10, 19),
                 description='Tăng volume, thêm drop set và super set. Protein 2g/kg thể trọng.'),
            dict(order=3, title='Giai đoạn 3 – Duy trì & đánh giá', is_completed=False,
                 start_date=date(2026, 10, 20), end_date=date(2026, 11, 24),
                 description='Giảm volume, tăng cường độ. Đo lại số đo cơ thể và điều chỉnh.'),
        ]

        for p in phases1:
            RoadmapPhase.objects.get_or_create(roadmap=roadmap1, order=p['order'], defaults=p)

        # Roadmap 2: Giảm cân (đã hoàn thành)
        roadmap2, _ = Roadmap.objects.get_or_create(
            user=user, title='Giảm mỡ hè 2026',
            defaults=dict(
                description='Giảm 5kg trong 8 tuần kết hợp deficit calo và cardio.',
                goal='weight_loss',
                start_date=date(2026, 7, 1),
                end_date=date(2026, 8, 26),
                is_active=False,
            )
        )

        phases2 = [
            dict(order=1, title='Tuần 1-4 – Cắt calo', is_completed=True,
                 start_date=date(2026, 7, 1), end_date=date(2026, 7, 28),
                 description='Deficit 500 calo/ngày, cardio 3 buổi/tuần 30 phút.'),
            dict(order=2, title='Tuần 5-8 – Duy trì cơ', is_completed=True,
                 start_date=date(2026, 7, 29), end_date=date(2026, 8, 26),
                 description='Tăng protein, giảm carb. Tập tạ 3 buổi + cardio 2 buổi.'),
        ]

        for p in phases2:
            RoadmapPhase.objects.get_or_create(roadmap=roadmap2, order=p['order'], defaults=p)

        self.stdout.write(f'  ✓ 2 roadmaps, 5 phases')

    # ──────────────────────────────────────────────────────────────────────────
    # JOURNAL
    # ──────────────────────────────────────────────────────────────────────────
    def _seed_journals(self, user):
        journals_data = [
            dict(
                journal=dict(
                    date=date(2026, 9, 1), title='Ngực + Vai',
                    notes='Buổi tập đầu tuần, năng lượng tốt. Bench press tăng được 2.5kg.',
                    duration_minutes=90, mood=4, calories_burned=420,
                ),
                exercises=[
                    dict(name='Bench Press', sets=4, reps=10, weight_kg=82.5),
                    dict(name='Incline Dumbbell Press', sets=3, reps=12, weight_kg=32),
                    dict(name='Cable Fly', sets=3, reps=15, weight_kg=15),
                    dict(name='Shoulder Press', sets=4, reps=10, weight_kg=50),
                    dict(name='Lateral Raise', sets=4, reps=15, weight_kg=10),
                ]
            ),
            dict(
                journal=dict(
                    date=date(2026, 9, 3), title='Lưng + Tay sau',
                    notes='Deadlift PR mới 120kg! Form giữ tốt. Tricep bơm máu nhiều.',
                    duration_minutes=95, mood=5, calories_burned=480,
                ),
                exercises=[
                    dict(name='Deadlift', sets=4, reps=5, weight_kg=120, notes='PR mới!'),
                    dict(name='Pull-up', sets=4, reps=8, weight_kg=None),
                    dict(name='Barbell Row', sets=4, reps=10, weight_kg=70),
                    dict(name='Face Pull', sets=3, reps=15, weight_kg=20),
                    dict(name='Tricep Pushdown', sets=3, reps=15, weight_kg=30),
                    dict(name='Skull Crusher', sets=3, reps=12, weight_kg=30),
                ]
            ),
            dict(
                journal=dict(
                    date=date(2026, 9, 5), title='Chân',
                    notes='Squat nặng, chân run nhưng hoàn thành. Đau đùi sau ngay từ hôm sau.',
                    duration_minutes=90, mood=3, calories_burned=520,
                ),
                exercises=[
                    dict(name='Squat', sets=4, reps=6, weight_kg=100),
                    dict(name='Leg Press', sets=4, reps=12, weight_kg=160),
                    dict(name='Romanian Deadlift', sets=3, reps=10, weight_kg=80),
                    dict(name='Leg Curl', sets=3, reps=12, weight_kg=45),
                    dict(name='Calf Raise', sets=4, reps=20, weight_kg=60),
                ]
            ),
            dict(
                journal=dict(
                    date=date(2026, 9, 7), title='Cardio + Core',
                    notes='Chạy nhẹ nhàng phục hồi sau ngày chân. Plank hold được 2 phút.',
                    duration_minutes=60, mood=4, calories_burned=350,
                ),
                exercises=[
                    dict(name='Chạy bộ', duration_seconds=1680, notes='5km – 28 phút'),
                    dict(name='Plank', sets=3, duration_seconds=120),
                    dict(name='Crunches', sets=3, reps=20),
                    dict(name='Leg Raise', sets=3, reps=15),
                ]
            ),
            dict(
                journal=dict(
                    date=date(2026, 9, 9), title='Ngực + Tay trước',
                    notes='Buổi tập cuối tuần. Tay trước pump tốt.',
                    duration_minutes=85, mood=4, calories_burned=400,
                ),
                exercises=[
                    dict(name='Incline Bench Press', sets=4, reps=10, weight_kg=70),
                    dict(name='Cable Fly', sets=3, reps=15, weight_kg=17.5),
                    dict(name='Dip', sets=3, reps=12),
                    dict(name='Barbell Curl', sets=4, reps=10, weight_kg=40),
                    dict(name='Hammer Curl', sets=3, reps=12, weight_kg=16),
                ]
            ),
        ]

        count_journals = 0
        count_exercises = 0

        for entry in journals_data:
            journal, created = TrainingJournal.objects.get_or_create(
                user=user,
                date=entry['journal']['date'],
                title=entry['journal']['title'],
                defaults=entry['journal'],
            )
            if created:
                exercises = [
                    JournalExercise(journal=journal, **ex)
                    for ex in entry['exercises']
                ]
                JournalExercise.objects.bulk_create(exercises)
                count_exercises += len(exercises)
            count_journals += 1

        self.stdout.write(f'  ✓ {count_journals} journals, {count_exercises} exercises')
