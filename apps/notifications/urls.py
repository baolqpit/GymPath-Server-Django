from django.urls import path
from .views import DeviceTokenView

# Base prefix: /api/v1/notifications/
urlpatterns = [
    path('device-token/', DeviceTokenView.as_view(), name='device-token'),
]
