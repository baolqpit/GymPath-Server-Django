from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TrainingSchedule
from .serializers import TrainingScheduleSerializer


# ══════════════════════════════════════════════════════════════════════════════
# GET  /api/v1/schedules/
# POST /api/v1/schedules/
# ══════════════════════════════════════════════════════════════════════════════

class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Schedule'],
        summary='Danh sách lịch tập',
        parameters=[
            OpenApiParameter('date', str, description='Lọc theo ngày (YYYY-MM-DD)'),
            OpenApiParameter('is_completed', bool, description='Lọc theo trạng thái hoàn thành'),
        ],
        responses={200: TrainingScheduleSerializer(many=True)},
    )
    def get(self, request):
        # TODO:
        # 1. queryset = TrainingSchedule.objects.filter(user=request.user)
        # 2. Filter tuỳ chọn:
        #    date = request.query_params.get('date')
        #    if date: queryset = queryset.filter(date=date)
        #    is_completed = request.query_params.get('is_completed')
        #    if is_completed is not None: queryset = queryset.filter(is_completed=...)
        # 3. serializer = TrainingScheduleSerializer(queryset, many=True)
        # 4. return Response(serializer.data)
        raise NotImplementedError

    @extend_schema(
        tags=['Schedule'],
        summary='Tạo lịch tập mới',
        request=TrainingScheduleSerializer,
        responses={201: TrainingScheduleSerializer},
    )
    def post(self, request):
        # TODO:
        # 1. serializer = TrainingScheduleSerializer(data=request.data)
        # 2. serializer.is_valid(raise_exception=True)
        # 3. serializer.save(user=request.user)   ← gán user tại đây
        # 4. return Response(serializer.data, status=201)
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# GET    /api/v1/schedules/<id>/
# PUT    /api/v1/schedules/<id>/
# PATCH  /api/v1/schedules/<id>/
# DELETE /api/v1/schedules/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, user):
        # TODO:
        # 1. return TrainingSchedule.objects.get(pk=pk, user=user)
        # 2. Nếu DoesNotExist → raise Http404 (from django.http import Http404)
        raise NotImplementedError

    @extend_schema(tags=['Schedule'], summary='Chi tiết lịch tập', responses={200: TrainingScheduleSerializer})
    def get(self, request, pk):
        # TODO:
        # 1. schedule = self._get_object(pk, request.user)
        # 2. serializer = TrainingScheduleSerializer(schedule)
        # 3. return Response(serializer.data)
        raise NotImplementedError

    @extend_schema(tags=['Schedule'], summary='Cập nhật toàn bộ lịch tập', request=TrainingScheduleSerializer, responses={200: TrainingScheduleSerializer})
    def put(self, request, pk):
        # TODO:
        # 1. schedule = self._get_object(pk, request.user)
        # 2. serializer = TrainingScheduleSerializer(schedule, data=request.data)
        # 3. serializer.is_valid(raise_exception=True) / serializer.save()
        # 4. return Response(serializer.data)
        raise NotImplementedError

    @extend_schema(tags=['Schedule'], summary='Cập nhật một phần lịch tập', request=TrainingScheduleSerializer, responses={200: TrainingScheduleSerializer})
    def patch(self, request, pk):
        # TODO:
        # 1. schedule = self._get_object(pk, request.user)
        # 2. serializer = TrainingScheduleSerializer(schedule, data=request.data, partial=True)
        # 3. serializer.is_valid(raise_exception=True) / serializer.save()
        # 4. return Response(serializer.data)
        raise NotImplementedError

    @extend_schema(tags=['Schedule'], summary='Xoá lịch tập', responses={204: None})
    def delete(self, request, pk):
        # TODO:
        # 1. schedule = self._get_object(pk, request.user)
        # 2. schedule.delete()
        # 3. return Response(status=204)
        raise NotImplementedError
