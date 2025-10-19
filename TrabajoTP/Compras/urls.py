from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # --- Autenticación ---
    path('api/auth/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # GET /api/auth/refresh
    path('api/auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # POST /api/auth/register
    path('api/auth/register', views.RegisterView.as_view(), name='auth_register'),
    # --- Perfil de Usuario ---
    # GET, POST, PUT /api/user/profile
    path('api/user/profile', views.UserProfileView.as_view(), name='user_profile'),
    # --- Productos (Consumiendo API Stock) ---
    # GET /api/product
    path('api/product', views.ProductListView.as_view(), name='product_list'),
    # GET /api/product/{id}
    path('api/product/<int:id>', views.ProductDetailView.as_view(), name='product_detail'),
    # --- Carrito ---
    # GET, POST, PUT, DELETE /api/shopcart
    path('api/shopcart', views.CartView.as_view(), name='shopcart'),
    # TODO: path('api/shopcart/<int:productId>', ... ) para borrar un ítem
    # --- Pedidos ---
    # POST /api/shopcart/checkout
    path('api/shopcart/checkout', views.CheckoutView.as_view(), name='checkout'),
    # TODO: /api/shopcart/history (para ver historial)
]