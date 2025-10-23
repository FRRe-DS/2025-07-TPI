
from django.urls import path
from django.urls import include
from .views import ProductDetailView
from .views import Inicio, lista_productos, RegisterView, LoginView
from .views import index_page, login_page, register_page, lista_productos, RegisterView, LoginView
urlpatterns = [
    path('', Inicio, name='Inicio'),
    path('', index_page, name='index_page'),
    path('login/', login_page, name='login_page'), # Nueva URL para la página de login
    path('register/', register_page, name='register_page'), # Nueva URL para la página de registro
    path('product/', lista_productos, name='lista_productos'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'), # Añadida ProductDetailView
]