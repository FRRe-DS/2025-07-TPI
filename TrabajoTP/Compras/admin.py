from django.contrib import admin
# 1. Importa los NUEVOS modelos que SÍ existen
from .models import Carrito, ItemCarrito, Pedido, ItemPedido

# 2. Registra esos modelos
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Pedido)
admin.site.register(ItemPedido)