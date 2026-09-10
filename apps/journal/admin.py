from django.contrib import admin

from .models import TrainingJournal, JournalExercise


class JournalExerciseInline(admin.TabularInline):
    model = JournalExercise
    extra = 1


@admin.register(TrainingJournal)
class TrainingJournalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'duration_minutes', 'mood', 'calories_burned']
    list_filter = ['mood', 'date']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'date'
    inlines = [JournalExerciseInline]


@admin.register(JournalExercise)
class JournalExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'journal', 'sets', 'reps', 'weight_kg']
    search_fields = ['name', 'journal__title']
