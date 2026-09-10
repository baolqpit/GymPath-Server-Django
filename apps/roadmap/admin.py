from django.contrib import admin

from .models import Roadmap, RoadmapPhase


class RoadmapPhaseInline(admin.TabularInline):
    model = RoadmapPhase
    extra = 1
    ordering = ['order']


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'goal', 'start_date', 'end_date', 'is_active']
    list_filter = ['goal', 'is_active']
    search_fields = ['title', 'user__username']
    inlines = [RoadmapPhaseInline]


@admin.register(RoadmapPhase)
class RoadmapPhaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'roadmap', 'order', 'start_date', 'end_date', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['title', 'roadmap__title']
