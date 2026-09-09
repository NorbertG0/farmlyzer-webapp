from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Wykresy
    path('stats/', views.stats, name='stats'),

    # Uprawy
    path('crops/', views.crops, name='crops'),
    path('crops/<int:pk>/', views.crop_detail, name='crop_detail'),
    path('crops/add', views.add_crops, name='add_crops'),
    path('crops/edit/<int:pk>/', views.edit_crop, name='edit_crop'),
    path('crops/delete/<int:pk>/', views.delete_crop, name='delete_crop'),

    # Eksporty do csv i pdf
    path('crops/export_crops_csv', views.export_crops_csv, name='export_crops_csv'),
    path('crops/export_crops_pdf', views.export_crops_pdf, name='export_crops_pdf'),

    # Wilgotność
    path('crops/add_measurement/<int:pk>/', views.add_moisture_measurement, name='add_moisture_measurement'),
    path('crops/edit_measurement/<int:pk>/', views.edit_moisture_measurement, name='edit_moisture_measurement'),
    path('crops/delete_measurement/<int:pk>/', views.delete_moisture_measurement, name='delete_moisture_measurement'),

    # Zabiegi
    path('crops/add_treatment/<int:pk>/', views.add_treatment, name='add_treatment'),
    path('crops/edit_treatment/<int:pk>/', views.edit_treatment, name='edit_treatment'),
    path('crops/delete_treatment/<int:pk>/', views.delete_treatment, name='delete_treatment'),

    # pH gleby
    path('crops/add_soil_ph/<int:pk>/', views.add_soil_ph, name='add_soil_ph'),
    path('crops/edit_soil_ph/<int:pk>/', views.edit_soil_ph, name='edit_soil_ph'),
    path('crops/delete_soil_ph/<int:pk>/', views.delete_soil_ph, name='delete_soil_ph'),

    # Pogoda
    path('weather/', views.weather, name='weather'),
    path('weather/add_temperature/', views.add_temperature, name='add_temperature'),
    path('weather/edit_temperature/<int:pk>/', views.edit_temperature, name='edit_temperature'),
    path('weather/delete_temperature/<int:pk>/', views.delete_temperature, name='delete_temperature'),
    path('weather/add_rainfall/', views.add_rainfall, name='add_rainfall'),
    path('weather/edit_rainfall/<int:pk>/', views.edit_rainfall, name='edit_rainfall'),
    path('weather/delete_rainfall/<int:pk>/', views.delete_rainfall, name='delete_rainfall'),

    # Raporty
    path('reports/', views.reports, name='reports'),
]