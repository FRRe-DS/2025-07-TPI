from django.urls import path
from . import views, api_views

urlpatterns = [
    # URLs para VISTAS HTML - ahora bajo /api/ también
    path('', views.index, name='index'),  # Esto será /api/
    path('login/', views.login_view, name='login'),  # Esto será /api/login/
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('productos/', views.lista_productos, name='productos'),
    path('carrito/', views.shopcart_view, name='shopcart'),
    path('ordenes/', views.orders_view, name='ordenes'),
    
    # URLs para APIs - ya están bajo /api/
    path('user/profile', api_views.user_profile_api, name='api_profile'),  # /api/user/profile
    path('shopcart/', api_views.shopcart_get, name='api_shopcart_get'),  # /api/shopcart/
    path('shopcart/items/', views.api_agregar_al_carrito, name='api_agregar_al_carrito'),  # /api/shopcart/items/
    path('shopcart/clear/', api_views.shopcart_clear, name='api_shopcart_clear'),
    path('shopcart/items/<int:productId>/', api_views.shopcart_remove_item, name='api_shopcart_remove'),
    path('shopcart/checkout/', api_views.checkout_api, name='api_checkout'),
    path('shopcart/history', api_views.order_history_api, name='api_order_history'),
    path('shopcart/history/<int:id>', api_views.order_detail_api, name='api_order_detail'),
    path('shopcart/history/<int:id>/cancel', api_views.cancel_order_api, name='api_cancel_order'),
    
    # API STOCK
    path('reservas', api_views.obtener_reservas_usuario, name='api_reservas'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto-detalle'),
]