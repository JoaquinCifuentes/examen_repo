from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('registro/', views.registro, name="registro"),
    path('login/', views.login, name="login"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('crearViaje/', views.crearViaje, name="crearViaje"),
    path('editar/<int:idViaje>', views.editar, name="editar"),
    path('detalle/<int:idViaje>', views.detalle, name="detalle"),
    path('eliminar/<int:idViaje>', views.eliminar, name="eliminar"),
    path('join/<int:idViaje>', views.join, name="join"),
    path('abortar/<int:idViaje>', views.abortar, name="abortar"),
    path('salir/', views.salir, name="salir"),
]
