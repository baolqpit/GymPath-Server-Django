from django.urls import path

from .views import (
    RoadmapListCreateView,
    RoadmapDetailView,
    PhaseListCreateView,
    PhaseDetailView,
)

# Base prefix: /api/v1/roadmaps/
urlpatterns = [
    path('', RoadmapListCreateView.as_view(), name='roadmap-list-create'),
    path('<int:pk>/', RoadmapDetailView.as_view(), name='roadmap-detail'),
    path('<int:roadmap_pk>/phases/', PhaseListCreateView.as_view(), name='phase-list-create'),
    path('<int:roadmap_pk>/phases/<int:pk>/', PhaseDetailView.as_view(), name='phase-detail'),
]
