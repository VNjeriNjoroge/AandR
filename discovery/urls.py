from django.urls import path
from .views import DiscoveryDashboard

urlpatterns = [
    path('artists/', DiscoveryDashboard.as_view(), name='discovery-dashboard'),
]