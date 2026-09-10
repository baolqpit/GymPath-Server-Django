from django.urls import path

from .views import (
    JournalListCreateView,
    JournalDetailView,
    ExerciseListCreateView,
    ExerciseDetailView,
)

# Base prefix: /api/v1/journals/
urlpatterns = [
    path('', JournalListCreateView.as_view(), name='journal-list-create'),
    path('<int:pk>/', JournalDetailView.as_view(), name='journal-detail'),
    path('<int:journal_pk>/exercises/', ExerciseListCreateView.as_view(), name='exercise-list-create'),
    path('<int:journal_pk>/exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise-detail'),
]
