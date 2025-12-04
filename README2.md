# Trabajo Práctico Integrador - Grupo 07

<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-Tercera%20Entrega-success?style=for-the-badge)
![UTN](https://img.shields.io/badge/UTN-FRRe-blue?style=for-the-badge)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

**Sistema Modular de Gestión de Stock y Portal de Ventas**
<br>
Desarrollo de Software 2025 - Tercera Entrega

[Reportar Bug](https://github.com/FRRe-DS/2025-07-TPI/issues) · [Solicitar Feature](https://github.com/FRRe-DS/2025-07-TPI/issues)

</div>

---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripcion)
2. [Arquitectura del Sistema](#arquitectura)
3. [Estructura del Repositorio](#estructura)
4. [Instalación y Despliegue](#instalacion)
5. [Dependencias](#dependencias)
6. [Ejecución](#ejecucion)
7. [Módulos y Funcionalidades](#modulos)
8. [API Documentation](#api)
9. [Modelos de Datos](#modelos)
10. [Tecnologías](#tecnologias)
11. [Contribución](#contribucion)
12. [Licencia](#licencia)

---

<a name="descripcion"></a>
## 📝 Descripción del Proyecto

Este proyecto implementa un sistema integral para la administración de inventarios y la gestión de pedidos de clientes en un entorno de e-commerce. Diseñado bajo un enfoque modular, el sistema permite desacoplar la lógica de negocio de la interfaz de usuario y la persistencia de datos.

El objetivo principal es simular un entorno real de e-commerce donde interactúan múltiples componentes: un portal de cara al cliente, un validador de reglas de negocio y un gestor de almacén. Esta tercera entrega incluye mejoras en la API de stock, gestión de bookings y integración con FastAPI para una mejor escalabilidad.

---

<a name="arquitectura"></a>
## Arquitectura del Sistema

El diseño sigue una arquitectura en capas para asegurar la escalabilidad y mantenibilidad del código:

- **Capa de Presentación**: Interfaz de usuario para simulación de compras.
- **Capa de Lógica de Negocio**: Validación de reglas, gestión de stock y bookings.
- **Capa de Datos**: Persistencia en memoria (simulada) de productos y reservas.

El sistema utiliza FastAPI para exponer una API RESTful que permite la interacción con el stock y la gestión de reservas de productos.

---

<a name="estructura"></a>
## Estructura del Repositorio

```
2025-07-TPI-feature-tercera-entrega/
├── LICENSE
└── TrabajoTP/
    ├──  .gitignore
    ├──  check_orders.py
    ├──  check_tables.py
    ├──  DATABASE_SETUP.md
    ├──  debug_db.py
    ├──  docker-compose.yml
    ├──  dockerfile
    ├──  env.ejemplo
    ├──  manage.py
    ├──  requirements.txt
    ├──  2025-07-TPI/
    │   ├── env
    ├──  portal_compras/
    │   ├── admin.py
    │   ├── api_views.py
    │   ├── apps.py
    │   ├── backends.py
    │   ├── keycloak_auth.py
    │   ├── models.py
    │   ├── pipeline.py
    │   ├── services.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── __init__.py
    │   ├── migrations/
    │       ├── 0001_initial.py
    │       ├── 0002_initial.py
    │       ├── __init__.py
    ├── realm-config/
    │    ├── realm.json
    ├── static/
    │    ├── portal_compras/
    │        ├── css/
    │            ├── css.css
    │            ├── producto.css
    ├── staticfiles/
    ├── templates/
    │   │   ├──portal_compras/
    │   │           carrito.html
    │   │           index.html
    │   │           login.html
    │   │           ordenes.html
    │   │           productos.html
    │   │           registro.html
    │   │           reservas.html
    │   │
    │   ├── TrabajoTP/
    │           asgi.py
    │           forms.py
    │           models.py
    │           settings.py
    │           urls.py
    │           views.py
    │           wsgi.py
    │           __init__.py

```
<a name="instalacion"></a>
##  Instalación y Despliegue

1. Ejecución con Docker Compose (Local)

  
  
  git clone https://github.com/FRRe-DS/2025-07-TPI.git
  
2. Navega al directorio del proyecto:
   ```bash
   cd TrabajoTP
   ```

3. Ejecuta los servicios:
   ```bash
   docker-compose up --build
   ```

4. Accede a la aplicación:
   - Portal de Compras: http://localhost:8000
   - API de Stock: http://localhost:8000/docs (si está integrada)
   - Admin Django: http://localhost:8000/admin

<a name="dependencias"></a>
## Dependencias

Las dependencias principales del proyecto se encuentran en `TrabajoTP/requirements.txt`:

- **FastAPI**: Framework para construir APIs REST con Python.
- **Uvicorn**: Servidor ASGI para FastAPI.
- **Pydantic**: Validación de datos y serialización.

<a name="ejecucion"></a>
##  Ejecución

Una vez instalado, puedes ejecutar la aplicación con:

```bash
    cd TrabajoTP
    docker-compose up --build

    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
```

Para desarrollo, el flag `--reload` permite recarga automática al cambiar el código.

<a name="modulos"></a>
## Módulos y Funcionalidades

### Portal de Ventas
Interfaz web desarrollada con Django que permite a los usuarios navegar el catálogo de productos, agregar items al carrito y realizar pedidos. Incluye páginas para productos, carrito, órdenes, login y registro.

### Gestión de Stock
API REST desarrollada con FastAPI para la administración del inventario. Gestiona productos, stock, precios y reservas. Endpoints para listar productos, obtener detalles y manejar bookings.

### Gestión de Usuarios y Autenticación
Sistema de autenticación integrado con Keycloak para login seguro y registro de usuarios. Perfiles de usuario con información adicional como teléfono, DNI y fecha de nacimiento.

### Gestión de Carritos de Compras
Funcionalidad para que los usuarios agreguen productos al carrito, calculen totales automáticamente y gestionen items antes de confirmar la compra. Persistencia en base de datos con JSONField.

### Gestión de Órdenes
Módulo completo para el manejo de órdenes de compra: creación desde el carrito, actualización de estados (pendiente, procesando, enviado, entregado, cancelado), integración con APIs de stock y logística, y tracking de envíos.

### Lógica de Negocio
Capa intermedia que valida reglas de negocio: verificación de stock disponible, precios correctos, registro de transacciones y gestión de bookings para evitar overbooking.

### Gestión de Bookings
Sistema de reservas de stock para pedidos pendientes. Permite crear reservas, vincular a órdenes, liberar stock si falla el proceso y mantener integridad del inventario.

### Integración con APIs Externas
Comunicación con servicios externos: API de Stock para reservas, API de Logística para tracking de envíos y Keycloak para autenticación.

<a name="api"></a>
## API Documentation

La API está documentada automáticamente con Swagger UI. Al ejecutar la aplicación, visita `http://localhost:8000/docs` para interactuar con los endpoints.

### Endpoints Principales

#### Productos
- `GET /api/product`: Lista todos los productos.
- `GET /api/product/{id}`: Obtiene un producto específico.

#### Bookings
- `POST /api/booking`: Crea una nueva reserva.
- `GET /api/booking/{id}`: Obtiene una reserva específica.
- `PUT /api/booking/{id}`: Vincula un pedido a una reserva.
- `POST /api/booking/{id}/release`: Libera una reserva y devuelve stock.

<a name="modelos"></a>
## Modelos de Datos

### Producto
```python
{
  "id": "string",
  "nombre": "string",
  "descripcion": "string (opcional)",
  "precio": {
    "amount": float,
    "currency": "ARS"
  },
  "pesoKg": float,
  "stock": int
}
```

### Booking
```python
{
  "bookingId": "string",
  "compraId": "string",
  "items": {
    "productId": "cantidad"
  },
  "estado": "reservado" | "liberado"
}
```
### UserProfile
```python
{
  "user": "OneToOneField(User, on_delete=models.CASCADE)",
  "phone": "CharField(max_length=20)",
  "dni": "CharField(max_length=15)",
  "birthDate": "DateField",
  "createdAt": "DateTimeField(auto_now_add=True)",
  "updatedAt": "DateTimeField(auto_now=True)"
}
```
### ShoppingCart
```python
{
  "user": "OneToOneField(User, on_delete=models.CASCADE, unique=True)",
  "items": "JSONField(default=list)",
  "total": "DecimalField(max_digits=10, decimal_places=2, default=0)",
  "created_at": "DateTimeField(auto_now_add=True)",
  "updated_at": "DateTimeField(auto_now=True)"
}
```
### Order 
```python
{
  "user": "ForeignKey(User, on_delete=models.CASCADE, related_name='orders')",
  "date": "DateTimeField(auto_now_add=True)",
  "total": "DecimalField(max_digits=10, decimal_places=2)",
  "delivery_address": "TextField",
  "payment_method": "CharField(max_length=50, choices=PAYMENT_METHODS)",
  "status": "CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')",
  "stock_booking_id": "CharField(max_length=100, null=True, blank=True)",
  "logistics_tracking_id": "CharField(max_length=100, null=True, blank=True)",
  "customer_notes": "TextField(blank=True, null=True)",
  "estimated_delivery": "DateField(null=True, blank=True)"
}
```
### OrderItem
```python
{
  "order": "ForeignKey(Order, related_name='items', on_delete=models.CASCADE)",
  "productId": "IntegerField",
  "product_name": "CharField(max_length=255, default='')",
  "quantity": "IntegerField",
  "price": "DecimalField(max_digits=10, decimal_places=2)",
  "created_at": "DateTimeField(auto_now_add=True)"
}
```

<a name="tecnologias"></a>
## Tecnologías

| Categoría          | Tecnología          | Uso                                      |
|--------------------|---------------------|------------------------------------------|
| Lenguaje          | Python 3.8+        | Lógica de backend y scripts.            |
| Framework         | FastAPI            | Construcción de APIs RESTful.           |
| Validación        | Pydantic           | Modelado y validación de datos.         |
| Infraestructura   | Docker             | Containerización y entorno reproducible.|
| Control de Versiones | Git               | Gestión del código fuente.              |
| Framework Web     | Django              | Desarrollo del portal de ventas.        |



## URLs de Acceso

### Producción

- **API de Stock**: https://stock.mmalgor.com.ar

- **Portal de Compras (Django)**: https://compras.mmalgor.com.ar
  - Páginas principales: / (inicio), /productos, /carrito, /login, /registro, /ordenes, /reservas, /admin

- **API de Logística**: https://apilogistica.mmalgor.com.ar

- **Keycloak (Autenticación)**: https://keycloak.mmalgor.com.ar

### Desarrollo

- **API de Stock y Portal de Compras**: http://localhost:8000
  - Documentación FastAPI: http://localhost:8000/docs

<a name="contribucion"></a>
## Contribución

Para contribuir al proyecto:

1. Fork el repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`).
4. Push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

<a name="licencia"></a>
## Licencia

Este proyecto es parte del Trabajo Práctico Integrador de la Universidad Tecnológica Nacional - Facultad Regional Resistencia. Todos los derechos reservados.

<div align="center"> 
<sub>Desarrollo de Software - TPI 2025 - Tercera Entrega</sub> 
</div>
