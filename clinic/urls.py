from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pacientes/', views.pacientes, name='pacientes'),
    path('tutores/', views.tutores, name='tutores'),
    path('veterinarios/', views.veterinarios, name='veterinarios'),
    path('informes/', views.informes, name='informes'),
    path('mascota/<int:pk>/', views.mascota_detalle, name='mascota_detalle'),
    path('nuevo/', views.nuevo_registro, name='nuevo_registro'),
]
