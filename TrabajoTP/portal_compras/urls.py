# portal_compras/urls.py
from django.urls import path
from . import views, api_views

urlpatterns = [
    # URLs para VISTAS HTML
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('productos/', views.lista_productos, name='productos'),
    path('carrito/', views.shopcart_view, name='shopcart'),
    path('ordenes/', views.orders_view, name='ordenes'),
    
    # API endpoints
    path('user/profile', api_views.user_profile_api, name='api_profile'),
    path('shopcart/', api_views.shopcart_get, name='api_shopcart_get'),
    path('shopcart/items/', views.api_agregar_al_carrito, name='api_agregar_al_carrito'),
    path('shopcart/clear/', api_views.shopcart_clear, name='api_shopcart_clear'),
    path('shopcart/items/<int:productId>/', api_views.shopcart_remove_item, name='api_shopcart_remove'),
    path('shopcart/checkout/', api_views.checkout_api, name='api_checkout'),
    path('shopcart/history', api_views.order_history_api, name='api_order_history'),
    path('shopcart/history/<int:id>', api_views.order_detail_api, name='api_order_detail'),
    path('shopcart/history/<int:id>/cancel', api_views.cancel_order_api, name='api_cancel_order'),
    
    # API STOCK
    path('reservas', api_views.obtener_reservas_usuario, name='api_reservas'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto-detalle'),
    
    # ----- API LOGÍSTICA ------
    path('api/envios', api_views.obtener_envios_logistica, name='api_envios'),  # Renombrada
    path('api/envios/crear', api_views.crear_envio_logistica, name='api_crear_envio'),
]