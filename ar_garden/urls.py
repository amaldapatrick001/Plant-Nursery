from django.urls import path
from . import views

app_name = 'ar_garden'
urlpatterns = [
    path('upload/', views.upload_field_image, name='upload_field'),
    path('select/<int:field_id>/', views.select_plant_positions, name='select_plants'),
    path('view-3d/<int:field_id>/', views.view_3d_garden, name='view_3d_garden'),
    path('optimize/<int:field_id>/', views.optimize_placement, name='optimize_placement'),
    path('check-plant-distance/<int:field_id>/', views.check_plant_distance, name='check_plant_distance'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/add/', views.add_plant_type, name='add_plant_type'),
]
