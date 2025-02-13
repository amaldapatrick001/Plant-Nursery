from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('forecast/', views.solar_forecast_view, name='solar_forecast'),
    path('api/forecast/', api.get_solar_forecast, name='solar_forecast_api'),
]
