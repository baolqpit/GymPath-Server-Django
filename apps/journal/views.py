from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import TrainingJournal, JournalExercise
from .serializers import TrainingJournalSerializer, JournalExerciseSerializer


# ══════════════════════════════════════════════════════════════════════════════
# GET  /api/v1/journals/
# POST /api/v1/journals/
# ══════════════════════════════════════════════════════════════════════════════

class JournalListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Journal'],
        summary='Danh sách nhật ký tập',
        parameters=[
            OpenApiParameter('date', str, description='Lọc theo ngày (YYYY-MM-DD)'),
            OpenApiParameter('month', str, description='Lọc theo tháng (YYYY-MM)'),
            OpenApiParameter('mood', int, description='Lọc theo mood (1-5)'),
        ],
        responses={200: TrainingJournalSerializer(many=True)},
    )
    def get(self, request):
        # TODO:
        # 1. queryset = TrainingJournal.objects.filter(user=request.user)
        #              .prefetch_related('exercises').select_related('schedule')
        # 2. Filter:
        #    date = request.query_params.get('date')
        #    if date: queryset = queryset.filter(date=date)
        #    month = request.query_params.get('month')  # format: "2026-09"
        #    if month: queryset = queryset.filter(date__year=..., date__month=...)
        #    mood = request.query_params.get('mood')
        #    if mood: queryset = queryset.filter(mood=mood)
        # 3. serializer = TrainingJournalSerializer(queryset, many=True)
        # 4. return Response(serializer.data)
        query = TrainingJournal.objects.filter(user=request.user).prefetch_related('exercises').select_related(
            'schedule')

        date = request.query_params.get('date', None)
        if date:
            query = query.filter(date=date)

        month = request.query_params.get('month', None)
        if month:
            year, m = month.split('-')
            query = query.filter(date__year=year, date__month=m)

        mood = request.query_params.get('mood', None)
        if mood:
            query = query.filter(mood=mood)

        serializer = TrainingJournalSerializer(query, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Journal'],
        summary='Tạo nhật ký tập mới (kèm exercises nếu có)',
        request=TrainingJournalSerializer,
        responses={201: TrainingJournalSerializer},
    )
    def post(self, request):
        # TODO:
        # 1. serializer = TrainingJournalSerializer(data=request.data)
        # 2. serializer.is_valid(raise_exception=True)
        # 3. serializer.save(user=request.user)
        # 4. return Response(serializer.data, status=201)
        serializer = TrainingJournalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
# GET/PUT/PATCH/DELETE /api/v1/journals/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class JournalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_object(pk, user):
        # TODO: Lấy journal theo pk và user, raise Http404 nếu không tìm thấy
        return get_object_or_404(
            TrainingJournal.objects.select_related("schedule").prefetch_related(
                "exercises"
            ),
            pk=pk,
            user=user,
        );

    @extend_schema(tags=['Journal'], summary='Chi tiết nhật ký tập', responses={200: TrainingJournalSerializer})
    def get(self, request, pk):
        # TODO:
        # 1. journal = self._get_object(pk, request.user)
        # 2. serializer = TrainingJournalSerializer(journal)
        # 3. return Response(serializer.data)
        journal = self._get_object(pk=pk, user=request.user)
        serializer = TrainingJournalSerializer(journal)
        return Response(serializer.data)

    @extend_schema(tags=['Journal'], summary='Cập nhật toàn bộ nhật ký', request=TrainingJournalSerializer,
                   responses={200: TrainingJournalSerializer})
    def put(self, request, pk):
        # TODO: Full update (bao gồm cả exercises nếu gửi kèm)
        journal = self._get_object(pk=pk, user=request.user)

        serializer = TrainingJournalSerializer(instance=journal, data=request.data, partial=False,
                                               context={'request': request})

        serializer.is_valid(raise_exception=True)

        updated_journal = serializer.save()

        return Response(TrainingJournalSerializer(updated_journal).data)

    @extend_schema(tags=['Journal'], summary='Cập nhật một phần nhật ký', request=TrainingJournalSerializer,
                   responses={200: TrainingJournalSerializer})
    def patch(self, request, pk):
        # TODO: Partial update (ví dụ: chỉ cập nhật mood hoặc notes)
        journal = self._get_object(pk=pk, user=request.user)

        serializer = TrainingJournalSerializer(
            instance=journal,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        updated_journal = serializer.save()

        return Response(TrainingJournalSerializer(updated_journal).data)

    @extend_schema(tags=['Journal'], summary='Xoá nhật ký tập', responses={204: None})
    def delete(self, request, pk):
        # TODO: Xoá journal (cascade xoá exercises theo)
        journal = self._get_object(pk=pk, user=request.user)

        journal.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════════════════════════════════
# GET  /api/v1/journals/<journal_id>/exercises/
# POST /api/v1/journals/<journal_id>/exercises/
# ══════════════════════════════════════════════════════════════════════════════

class ExerciseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_journal(journal_pk, user):
        # TODO: Lấy journal, kiểm tra owner
        return get_object_or_404(TrainingJournal, pk=journal_pk, user=user)

    @extend_schema(tags=['Journal – Exercise'], summary='Danh sách bài tập trong nhật ký',
                   responses={200: JournalExerciseSerializer(many=True)})
    def get(self, request, journal_pk):
        # TODO:
        # 1. journal = self._get_journal(journal_pk, request.user)
        # 2. exercises = journal.exercises.all()
        # 3. serializer = JournalExerciseSerializer(exercises, many=True)
        # 4. return Response(serializer.data)
        journal = self._get_journal(journal_pk, request.user)
        exercises = journal.exercises.all()
        serializer = JournalExerciseSerializer(exercises, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(tags=['Journal – Exercise'], summary='Thêm bài tập vào nhật ký', request=JournalExerciseSerializer,
                   responses={201: JournalExerciseSerializer})
    def post(self, request, journal_pk):
        # TODO:
        # 1. journal = self._get_journal(journal_pk, request.user)
        # 2. serializer = JournalExerciseSerializer(data=request.data)
        # 3. serializer.is_valid(raise_exception=True)
        # 4. serializer.save(journal=journal)
        # 5. return Response(serializer.data, status=201)
        journal = self._get_journal(journal_pk, request.user)
        serializer = JournalExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(journal=journal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
# GET/PUT/PATCH/DELETE /api/v1/journals/<journal_id>/exercises/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class ExerciseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_exercise(journal_pk, pk, user):
        # TODO:
        # 1. Lấy exercise theo pk, journal__pk=journal_pk, journal__user=user
        # 2. raise Http404 nếu không tìm thấy
        return get_object_or_404(
            JournalExercise,
            pk=pk,
            journal__pk=journal_pk,
            journal__user=user
        )

    @extend_schema(tags=['Journal – Exercise'], summary='Chi tiết bài tập', responses={200: JournalExerciseSerializer})
    def get(self, request, journal_pk, pk):
        exercise = self._get_exercise(journal_pk, pk, request.user)
        serializer = JournalExerciseSerializer(exercise)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Journal – Exercise'], summary='Cập nhật toàn bộ bài tập', request=JournalExerciseSerializer,
                   responses={200: JournalExerciseSerializer})
    def put(self, request, journal_pk, pk):
        exercise = self._get_exercise(journal_pk, pk, request.user)
        serializer = JournalExerciseSerializer(exercise, data=request.data, partial=False, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Journal – Exercise'], summary='Cập nhật một phần bài tập', request=JournalExerciseSerializer,
                   responses={200: JournalExerciseSerializer})
    def patch(self, request, journal_pk, pk):
        exercise = self._get_exercise(journal_pk, pk, request.user)
        serializer = JournalExerciseSerializer(
            instance=exercise,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Journal – Exercise'], summary='Xoá bài tập khỏi nhật ký', responses={204: None})
    def delete(self, request, journal_pk, pk):
        exercise = self._get_exercise(journal_pk, pk, request.user)
        exercise.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
