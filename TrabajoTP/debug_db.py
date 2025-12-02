import os
import django
import psycopg2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrabajoTP.settings')
django.setup()

from django.db import connection
from django.conf import settings

print("\n=== CONFIGURACIÓN DE BASE DE DATOS ===")
print(f"Base de datos por defecto: {settings.DATABASES['default']}")

# Información de conexión Django
db_config = settings.DATABASES['default']
print(f"\nConectando a:")
print(f"  Host: {db_config['HOST']}")
print(f"  Puerto: {db_config['PORT']}")
print(f"  BD: {db_config['NAME']}")
print(f"  Usuario: {db_config['USER']}")

# Probar conexión directa con psycopg2
try:
    direct_conn = psycopg2.connect(
        host=db_config['HOST'],
        port=db_config['PORT'],
        database=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD']
    )
    direct_cursor = direct_conn.cursor()
    
    print("\n✅ Conexión exitosa a Supabase")
    
    # Listar todas las tablas
    direct_cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = direct_cursor.fetchall()
    print(f"\nTablas en Supabase ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Contar órdenes directamente
    direct_cursor.execute("SELECT COUNT(*) FROM portal_compras_order")
    order_count = direct_cursor.fetchone()[0]
    print(f"\n📊 Órdenes en portal_compras_order: {order_count}")
    
    if order_count > 0:
        direct_cursor.execute("SELECT id, user_id, total, status, date FROM portal_compras_order")
        orders = direct_cursor.fetchall()
        print("\nDetalles de órdenes:")
        for order in orders:
            print(f"  - ID: {order[0]}, User: {order[1]}, Total: {order[2]}, Status: {order[3]}, Date: {order[4]}")
    
    direct_cursor.close()
    direct_conn.close()
    
except Exception as e:
    print(f"\n❌ Error conectando a Supabase: {e}")

# También verificar con Django ORM
print("\n=== VERIFICACIÓN CON DJANGO ORM ===")
from portal_compras.models import Order

orders_django = Order.objects.all()
print(f"Órdenes encontradas por Django ORM: {len(orders_django)}")

if orders_django:
    for order in orders_django:
        print(f"  - ID: {order.id}, Usuario: {order.user.username}, Total: {order.total}")
