from django.urls import path
from .views import CheckConnectionView, GetSSIDsView, UpdateSSIDView

urlpatterns = [
    path('check-connection/<str:ip>/', CheckConnectionView.as_view(), name='check-connection'),
    path('get-ssids/<str:ip>/', GetSSIDsView.as_view(), name='get-ssids'),
    path('update-ssid/', UpdateSSIDView.as_view(), name='update_ssid'),
]
