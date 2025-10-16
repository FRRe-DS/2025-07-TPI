
from django.urls import path
from django.urls import include

from .views import Inicio, crear_Producto, producto, buscar_producto
urlpatterns = [
    path('', Inicio, name='Inicio'),
    path('crear_producto/', crear_Producto, name='crear_producto'),
    path('producto/', producto, name='producto'),
    path('producto/buscar', buscar_producto, name='buscar_producto'),
]