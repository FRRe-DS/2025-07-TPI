from django.urls import path
from . import api_views
from . import views

urlpatterns = [
    # URLs para VISTAS HTML (páginas web)
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('productos/', views.lista_productos, name='productos'),  # ✅ Esta es la vista HTML
    path('carrito/', views.shopcart_view, name='shopcart'),
    path('ordenes/', views.orders_view, name='ordenes'),

    # URLs para APIs de Compras
    path('api/user/profile', api_views.user_profile_api, name='api_profile'),
    path('api/shopcart', api_views.shopcart_get, name='api_shopcart_get'),
    path('api/shopcart/items', api_views.shopcart_update, name='api_shopcart_update'),
    path('api/shopcart/clear', api_views.shopcart_clear, name='api_shopcart_clear'),
    path('api/shopcart/items/<int:productId>', api_views.shopcart_remove_item, name='api_shopcart_remove'),
    path('api/shopcart/checkout', api_views.checkout_api, name='api_checkout'),
    path('api/shopcart/history', api_views.order_history_api, name='api_order_history'),
    path('api/shopcart/history/<int:id>', api_views.order_detail_api, name='api_order_detail'),
    path('api/shopcart/history/<int:id>/cancel', api_views.cancel_order_api, name='api_cancel_order'),

    # ----- API STOCK ------ #
    # ✅ Mantén solo el detalle de producto si lo necesitas:
    path('api/productos/<int:producto_id>/', views.producto_detalle, name='producto-detalle'),
]