from django.urls import path
from .views import WeatherDetailView, WeatherHistoryView

urlpatterns = [
    path('weather/', WeatherDetailView.as_view(), name='weather-detail'),
    path('weather/history/', WeatherHistoryView.as_view(), name='weather-history'),
]
