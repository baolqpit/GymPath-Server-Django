from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Roadmap, RoadmapPhase
from .serializers import RoadmapSerializer, RoadmapPhaseSerializer


# ══════════════════════════════════════════════════════════════════════════════
# GET  /api/v1/roadmaps/
# POST /api/v1/roadmaps/
# ══════════════════════════════════════════════════════════════════════════════

class RoadmapListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Roadmap'],
        summary='Danh sách lộ trình',
        parameters=[
            OpenApiParameter('is_active', bool, description='Lọc lộ trình đang thực hiện'),
        ],
        responses={200: RoadmapSerializer(many=True)},
    )
    def get(self, request):
        # TODO:
        # 1. queryset = Roadmap.objects.filter(user=request.user).prefetch_related('phases')
        # 2. Filter: is_active = request.query_params.get('is_active')
        # 3. serializer = RoadmapSerializer(queryset, many=True)
        # 4. return Response(serializer.data)
        query = Roadmap.objects.filter(user=request.user).prefetch_related('phases')

        is_active = request.query_params.get('is_active', None)

        if is_active:
            query = query.filter(is_active=True)

        serializer = RoadmapSerializer(query, many=True)

        return Response(serializer.data)

    @extend_schema(
        tags=['Roadmap'],
        summary='Tạo lộ trình mới',
        request=RoadmapSerializer,
        responses={201: RoadmapSerializer},
    )
    def post(self, request):
        # TODO:
        # 1. serializer = RoadmapSerializer(data=request.data)
        # 2. serializer.is_valid(raise_exception=True)
        # 3. serializer.save(user=request.user)
        # 4. return Response(serializer.data, status=201)
        serializer = RoadmapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
# GET/PUT/PATCH/DELETE /api/v1/roadmaps/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class RoadmapDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_object(pk, user):
        # TODO: Lấy Roadmap theo pk và user, raise Http404 nếu không tìm thấy
        return get_object_or_404(Roadmap.objects.prefetch_related('phases'), pk=pk, user=user)

    @extend_schema(tags=['Roadmap'], summary='Chi tiết lộ trình', responses={200: RoadmapSerializer})
    def get(self, request, pk):
        # TODO:
        # 1. roadmap = self._get_object(pk, request.user)
        # 2. serializer = RoadmapSerializer(roadmap)
        # 3. return Response(serializer.data)
        roadmap = self._get_object(pk, request.user)
        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data)

    @extend_schema(tags=['Roadmap'], summary='Cập nhật toàn bộ lộ trình', request=RoadmapSerializer, responses={200: RoadmapSerializer})
    def put(self, request, pk):
        # TODO: Full update
        roadmap = self._get_object(pk, request.user)

        serializer = RoadmapSerializer(roadmap, data=request.data, partial=False, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Roadmap'], summary='Cập nhật một phần lộ trình', request=RoadmapSerializer, responses={200: RoadmapSerializer})
    def patch(self, request, pk):
        # TODO: Partial update (ví dụ: đổi is_active=False khi hoàn thành lộ trình)
        roadmap = self._get_object(pk, request.user)

        serializer = RoadmapSerializer(roadmap, data=request.data, partial=True, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Roadmap'], summary='Xoá lộ trình', responses={204: None})
    def delete(self, request, pk):
        # TODO: Xoá lộ trình (cascade xoá phases theo)
        roadmap = self._get_object(pk, request.user)

        roadmap.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════════════════════════════════
# GET  /api/v1/roadmaps/<roadmap_id>/phases/
# POST /api/v1/roadmaps/<roadmap_id>/phases/
# ══════════════════════════════════════════════════════════════════════════════

class PhaseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_roadmap(roadmap_pk, user):
        # TODO: Lấy Roadmap, kiểm tra owner, raise Http404 nếu cần
        return get_object_or_404(Roadmap, pk=roadmap_pk, user=user)

    @extend_schema(tags=['Roadmap – Phase'], summary='Danh sách giai đoạn của lộ trình', responses={200: RoadmapPhaseSerializer(many=True)})
    def get(self, request, roadmap_pk):
        # TODO:
        # 1. roadmap = self._get_roadmap(roadmap_pk, request.user)
        # 2. phases = roadmap.phases.all()
        # 3. serializer = RoadmapPhaseSerializer(phases, many=True)
        # 4. return Response(serializer.data)
        roadmap = self._get_roadmap(roadmap_pk, request.user)

        phases = roadmap.phases.all()

        serializer = RoadmapPhaseSerializer(phases, many=True)

        return Response(serializer.data)

    @extend_schema(tags=['Roadmap – Phase'], summary='Thêm giai đoạn vào lộ trình', request=RoadmapPhaseSerializer, responses={201: RoadmapPhaseSerializer})
    def post(self, request, roadmap_pk):
        # TODO:
        # 1. roadmap = self._get_roadmap(roadmap_pk, request.user)
        # 2. serializer = RoadmapPhaseSerializer(data=request.data)
        # 3. serializer.is_valid(raise_exception=True)
        # 4. serializer.save(roadmap=roadmap)
        # 5. return Response(serializer.data, status=201)
        roadmap = self._get_roadmap(roadmap_pk, request.user)

        serializer = RoadmapPhaseSerializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer.save(roadmap=roadmap)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
# GET/PUT/PATCH/DELETE /api/v1/roadmaps/<roadmap_id>/phases/<id>/
# ══════════════════════════════════════════════════════════════════════════════

class PhaseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get_phase(roadmap_pk, pk, user):
        # TODO:
        # 1. Lấy phase theo pk và roadmap__pk=roadmap_pk và roadmap__user=user
        # 2. raise Http404 nếu không tìm thấy
        return get_object_or_404(RoadmapPhase, roadmap__pk=roadmap_pk, pk=pk, roadmap__user=user)

    @extend_schema(tags=['Roadmap – Phase'], summary='Chi tiết giai đoạn', responses={200: RoadmapPhaseSerializer})
    def get(self, request, roadmap_pk, pk):
        phase = self._get_phase(roadmap_pk, pk, request.user)

        serializer = RoadmapPhaseSerializer(phase, many=False)

        return Response(serializer.data)

    @extend_schema(tags=['Roadmap – Phase'], summary='Cập nhật toàn bộ giai đoạn', request=RoadmapPhaseSerializer, responses={200: RoadmapPhaseSerializer})
    def put(self, request, roadmap_pk, pk):
        phase = self._get_phase(roadmap_pk, pk, request.user)

        serializer = RoadmapPhaseSerializer(phase, data=request.data, partial=False, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Roadmap – Phase'], summary='Cập nhật một phần giai đoạn', request=RoadmapPhaseSerializer, responses={200: RoadmapPhaseSerializer})
    def patch(self, request, roadmap_pk, pk):
        phase = self._get_phase(roadmap_pk, pk, request.user)

        serializer = RoadmapPhaseSerializer(phase, data=request.data, partial=True, context={'request': request})

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Roadmap – Phase'], summary='Xoá giai đoạn', responses={204: None})
    def delete(self, request, roadmap_pk, pk):
        phase = self._get_phase(roadmap_pk, pk, request.user)

        phase.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
