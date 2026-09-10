from django.contrib import admin

from .models import TrainingSchedule


@admin.register(TrainingSchedule)
class TrainingScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'start_time', 'difficulty', 'is_completed']
    list_filter = ['is_completed', 'difficulty', 'date']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'date'
