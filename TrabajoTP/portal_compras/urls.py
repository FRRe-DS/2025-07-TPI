from django.urls import path
from . import api_views

urlpatterns = [
    # Auth APIs
    path('auth/login', api_views.login_api, name='api_login'),
    path('auth/register', api_views.register_api, name='api_register'),
    path('user/profile', api_views.user_profile_api, name='api_profile'),
    
    # Shopping Cart APIs
    path('shopcart', api_views.shopcart_get, name='api_shopcart_get'),           # GET
    path('shopcart/items', api_views.shopcart_update, name='api_shopcart_update'), # POST/PUT
    path('shopcart/clear', api_views.shopcart_clear, name='api_shopcart_clear'), # DELETE
    path('shopcart/items/<int:productId>', api_views.shopcart_remove_item, name='api_shopcart_remove'), # DELETE item
    path('shopcart/checkout', api_views.checkout_api, name='api_checkout'),
    path('shopcart/history', api_views.order_history_api, name='api_order_history'),
    path('shopcart/history/<int:id>', api_views.order_detail_api, name='api_order_detail'),
    path('shopcart/history/<int:id>/cancel', api_views.cancel_order_api, name='api_cancel_order'),
]