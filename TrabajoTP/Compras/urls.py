
from django.urls import path
from django.urls import include

from .views import Inicio, crear_Producto
urlpatterns = [
    path('Inicio/', Inicio, name='Inicio'),
    path('crear_producto/', crear_Producto),
]