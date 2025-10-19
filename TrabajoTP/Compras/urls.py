
from django.urls import path
from django.urls import include

from .views import Inicio, lista_productos, RegisterView, login_view
urlpatterns = [
    path('', Inicio, name='Inicio'),
    path('product/', lista_productos, name='lista_productos'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
]