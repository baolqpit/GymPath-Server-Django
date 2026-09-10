from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# ── API v1 Routes ──────────────────────────────────────────────────────────────
# /api/v1/auth/      → apps.authentication.urls  (register, login, refresh, logout, me)
# /api/v1/schedules/ → apps.schedule.urls         (CRUD lịch tập)
# /api/v1/roadmaps/  → apps.roadmap.urls          (CRUD lộ trình + phases)
# /api/v1/journals/  → apps.journal.urls          (CRUD nhật ký tập)
#
# ── Docs ──────────────────────────────────────────────────────────────────────
# /api/schema/       → OpenAPI schema (JSON/YAML)
# /api/docs/         → Swagger UI
# /api/redoc/        → ReDoc UI

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/schedules/', include('apps.schedule.urls')),
    path('api/v1/roadmaps/', include('apps.roadmap.urls')),
    path('api/v1/journals/', include('apps.journal.urls')),

    # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
