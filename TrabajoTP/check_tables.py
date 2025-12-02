import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrabajoTP.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cursor.fetchall()

print('\n=== TABLAS EN LA BASE DE DATOS ===\n')
for table in tables:
    print(f'  • {table[0]}')

# Mostrar tablas de Django relacionadas con órdenes
print('\n=== TABLAS DE ÓRDENES ===\n')
order_tables = [t for t in tables if 'order' in t[0].lower()]
for table in order_tables:
    print(f'  • {table[0]}')

# Verificar si existen las tablas de portal_compras
print('\n=== ESTADO DE MIGRACIONES ===\n')
cursor.execute("SELECT name FROM django_migrations WHERE app = 'portal_compras'")
migrations = cursor.fetchall()
if migrations:
    print(f'  ✓ Migraciones de portal_compras aplicadas: {len(migrations)} migraciones')
    for mig in migrations:
        print(f'    - {mig[0]}')
else:
    print('  ✗ NO hay migraciones de portal_compras aplicadas')
