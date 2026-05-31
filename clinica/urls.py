from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('consulta/<int:pk>/', views.consulta_detalle, name='consulta_detalle'),
    path('consulta/<int:pk>/estado/', views.consulta_estado, name='consulta_estado'),
    path('paciente/<int:pk>/editar/', views.paciente_editar, name='paciente_editar'),
    path('tutor/<int:pk>/editar/', views.tutor_editar, name='tutor_editar'),
]
