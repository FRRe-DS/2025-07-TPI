# Guía de Configuración - Portal de Compras

## Configuración Inicial

1. Crear archivo `.env` en la raíz del proyecto con:

DB_NAME=portal_db
DB_USER=portal_user
DB_PASS=portal_password
DB_HOST=db
DB_PORT=5432
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=ds-2025-realm
KEYCLOAK_CLIENT_ID=grupo-07
KEYCLOAK_CLIENT_SECRET=tdSnJM8CsPPl6dJW4Tq6k9JWnSqndkfH

## Levantar el Proyecto

Ejecutar: docker-compose up -d --build

Esperar 2-3 minutos para que Keycloak inicialice completamente.

## Configuración de Base de Datos

Ejecutar: docker-compose exec web python manage.py migrate

## Configuración de Keycloak

1. Acceder a http://localhost:8080
   - Usuario: admin
   - Contraseña: ds2025

2. Verificar que exista el Realm "ds-2025-realm"

3. Configurar el Cliente "grupo-07":
   - Access Type: public
   - Valid Redirect URIs: http://localhost:8000/social-auth/complete/keycloak/*
   - Web Origins: http://localhost:8000

4. En Realm Settings → Login habilitar:
   - User registration
   - Forgot password
   - Remember me

## Uso de la Aplicación

1. Acceder a http://localhost:8000
2. Click en "Login" → "Iniciar Sesión con Keycloak"
3. Registrar nuevo usuario o iniciar sesión
4. Navegar productos y utilizar el carrito de compras

## URLs Importantes

- Aplicación: http://localhost:8000
- Admin Keycloak: http://localhost:8080
- API Carrito: http://localhost:8000/api/shopcart

## Comandos de Mantenimiento

Iniciar servicios: docker-compose up -d
Detener servicios: docker-compose down
Reiniciar Keycloak: docker-compose restart keycloak
Ver logs: docker-compose logs -f web
