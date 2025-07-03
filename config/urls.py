
from django.contrib import admin
from django.urls import path

from core.views import QueryView, HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/query/', QueryView.as_view(), name='query'),
    path('api/v1/health/', HealthCheckView.as_view(),name='health'),
]
