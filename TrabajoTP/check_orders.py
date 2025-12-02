import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrabajoTP.settings')
django.setup()

from django.db import connection
from portal_compras.models import Order, OrderItem

# Verificar si existen órdenes en Supabase
orders = Order.objects.all()
print(f"\n=== ÓRDENES EN LA BASE DE DATOS ===")
print(f"Total de órdenes: {len(orders)}")

if orders:
    for order in orders:
        print(f"\n  Orden #{order.id}")
        print(f"    Usuario: {order.user.username}")
        print(f"    Fecha: {order.date}")
        print(f"    Total: ${order.total}")
        print(f"    Estado: {order.status}")
        print(f"    Dirección: {order.delivery_address}")
        
        items = order.items.all()
        print(f"    Items: {len(items)}")
        for item in items:
            print(f"      - Producto ID: {item.productId}, Qty: {item.quantity}, Precio: ${item.price}")
else:
    print("\n❌ NO HAY ÓRDENES GUARDADAS EN LA BD")

# Verificar conexión a BD
print(f"\n=== INFORMACIÓN DE CONEXIÓN ===")
cursor = connection.cursor()
cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
databases = cursor.fetchall()
print(f"Base de datos conectada: {connection.get_connection_params()['dbname']}")
print(f"Host: {connection.get_connection_params()['host']}")
