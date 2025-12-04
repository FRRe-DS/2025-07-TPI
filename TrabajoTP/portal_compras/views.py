from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import requests
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import get_object_or_404

# Configuración Keycloak
KEYCLOAK_SERVER_URL = settings.KEYCLOAK_SERVER_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID

# =============================================================================
# VISTAS PRINCIPALES (PÁGINAS HTML)
# =============================================================================

def index(request):
    """Página principal con productos destacados"""
    productos_destacados = []
    
    try:
        # Obtener token para la API (client credentials para no autenticados)
        access_token = None
        
        if request.user.is_authenticated:
            # Intentar con token de usuario autenticado
            try:
                social_auth = request.user.social_auth.get(provider='keycloak')
                access_token = social_auth.extra_data['access_token']
                print(f"🔄 Home: Usando token de usuario {request.user.username}")
            except Exception as e:
                print(f"❌ Home: Error con token de usuario: {e}")
                access_token = None
        
        # Si no hay token de usuario, usar client credentials
        if not access_token:
            from .keycloak_auth import obtener_token_client_credentials
            access_token = obtener_token_client_credentials()
            print("🔄 Home: Usando client credentials")
        
        if access_token:
            stock_url = "https://stock.mmalgor.com.ar/v1/productos"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(stock_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                productos_api = response.json()
                print(f"✅ Home: {len(productos_api)} productos obtenidos")
                
                # Procesar todos los productos
                todos_productos = []
                
                for producto in productos_api:
                    categoria_principal = 'General'
                    if producto.get('categorias') and len(producto['categorias']) > 0:
                        categoria_principal = producto['categorias'][0].get('nombre', 'General')
                    
                    imagen_principal = None
                    if producto.get('imagenes') and len(producto['imagenes']) > 0:
                        for img in producto['imagenes']:
                            if img.get('esPrincipal'):
                                imagen_principal = img.get('url')
                                break
                        if not imagen_principal:
                            imagen_principal = producto['imagenes'][0].get('url')
                    
                    producto_formateado = {
                        'id': producto.get('id'),
                        'name': producto.get('nombre'),
                        'description': producto.get('descripcion', ''),
                        'price': float(producto.get('precio', 0)),
                        'stock': producto.get('stockDisponible', 0),
                        'category': categoria_principal,
                        'imagen_url': imagen_principal,
                        'ubicacion_ciudad': producto.get('ubicacion', {}).get('ciudad', ''),
                        'ubicacion_provincia': producto.get('ubicacion', {}).get('provincia', ''),
                    }
                    
                    todos_productos.append(producto_formateado)
                
                # ESTRATEGIA 1: Productos con mayor stock (más disponibles)
                productos_con_stock = [p for p in todos_productos if p['stock'] > 0]
                
                if productos_con_stock:
                    # Ordenar por stock descendente y tomar los primeros 8
                    productos_destacados = sorted(productos_con_stock, key=lambda x: x['stock'], reverse=True)[:8]
                else:
                    # Si no hay productos con stock, tomar los primeros 8
                    productos_destacados = todos_productos[:8]
                    
                print(f"🏠 Home: Mostrando {len(productos_destacados)} productos destacados")
                
            else:
                print(f"❌ Home: Error Stock API: {response.status_code}")
        else:
            print("❌ Home: No se pudo obtener token")
            
    except Exception as e:
        print(f"💥 Home: Error general: {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'portal_compras/index.html', {
        'user': request.user if request.user.is_authenticated else None,
        'productos_destacados': productos_destacados
    })
    
def login_view(request):
    """Vista de login que muestra opciones de autenticación"""
    if request.user.is_authenticated:
        return redirect('index')
    
    return render(request, 'portal_compras/login.html', {
        'keycloak_enabled': True,
        'keycloak_url': f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth'
    })

def registro_view(request):
    """Redirige a Keycloak para registro"""
    keycloak_registro_url = (
        f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/"
        f"protocol/openid-connect/registrations"
        f"?client_id={KEYCLOAK_CLIENT_ID}&response_type=code&scope=openid profile email&redirect_uri=https://keycloak.mmalgor.com.ar//social-auth/complete/keycloak/"
    )
    return redirect(keycloak_registro_url)

def logout_view(request):
    """Cerrar sesión tanto en Django como en Keycloak"""
    is_keycloak_user = False
    if hasattr(request, 'user') and request.user.is_authenticated:
        social_auth = getattr(request.user, 'social_auth', None)
        if social_auth and social_auth.filter(provider='keycloak').exists():
            is_keycloak_user = True
    
    auth_logout(request)
    
    if is_keycloak_user:
        keycloak_logout_url = (
            f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/"
            f"protocol/openid-connect/logout"
        )
        response = redirect(keycloak_logout_url)
    else:
        response = redirect('index')
    
    response['Location'] += '?clear_storage=true'
    return response

def shopcart_view(request):
    """Página del carrito - SOLO del usuario autenticado"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        carrito = get_user_cart(request.user)
        
        # Transformar los datos al formato que espera el template
        items_formateados = []
        total_calculado = 0
        
        for item in carrito.items:
            # Obtener datos originales
            cantidad = item.get('cantidad', 0)
            precio = item.get('producto', {}).get('price', 0)
            subtotal = cantidad * precio
            
            # Sumar al total
            total_calculado += subtotal
            
            # Crear item formateado
            items_formateados.append({
                'productId': item.get('producto_id'),
                'quantity': cantidad,
                'product': {
                    'id': item.get('producto', {}).get('id'),
                    'name': item.get('producto', {}).get('name'),
                    'price': precio,
                    'description': item.get('producto', {}).get('description'),
                    'imagen_url': item.get('producto', {}).get('imagen_url')
                },
                'subtotal': subtotal
            })
        
        # También calcular usando el método del carrito por si acaso
        carrito_total = carrito.calculate_total()
        
        print(f"🛒 DEBUG - Total calculado manualmente: {total_calculado}")
        print(f"🛒 DEBUG - Total del carrito.calculate_total(): {carrito_total}")
        
        # Usar el mayor de los dos totales (o el manual si hay diferencia)
        total_final = max(total_calculado, carrito_total)
        
        carrito_data = {
            'items': items_formateados,
            'total': total_final
        }
        
        # Actualizar el total en la base de datos
        if total_calculado != carrito_total:
            print(f"🛒 AJUSTANDO total en BD: {carrito_total} -> {total_calculado}")
            carrito.total = total_calculado
            carrito.save()
        
    except Exception as e:
        print(f"❌ Error en shopcart_view: {e}")
        import traceback
        traceback.print_exc()
        carrito_data = {'items': [], 'total': 0}
    
    return render(request, 'portal_compras/carrito.html', {
        'carrito': carrito_data,
        'user': request.user
    })

def orders_view(request):
    """Vista para el historial de órdenes"""
    orders_data = []
    
    if request.user.is_authenticated:
        try:
            from .models import Order, OrderItem
            from django.utils import timezone
            from datetime import timedelta
            
            orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-date')
            
            for order in orders:
                datos_envio = None
                # ✅ ACTUALIZAR ESTADO SOLO CON SHIPPING_ID
                if order.logistics_tracking_id and order.status in ['PENDING', 'PROCESSING', 'IN_TRANSIT']:
                    print(f"   🔄 Consultando estado para shipping_id: {order.logistics_tracking_id}")
                    
                    datos_envio = consultar_estado_envio_logistica(order.logistics_tracking_id)
                    
                    if datos_envio:
                        estado_logistica = datos_envio.get('status')
                        estado_mapeado = mapear_estado_logistica(estado_logistica)
                        
                        if estado_mapeado and estado_mapeado != order.status:
                            print(f"   ✅ Estado actualizado: {order.status} → {estado_mapeado}")
                            order.status = estado_mapeado
                            order.save()
                
                # Construir datos de la orden
                order_data = {
                    'id': order.id,
                    'date': order.date.isoformat(),
                    'status': order.status,
                    'status_display': obtener_display_estado(order.status),
                    'total': float(order.total),
                    'delivery_address': order.delivery_address,
                    'payment_method': order.payment_method,
                    'stock_booking_id': order.stock_booking_id,
                    'shipping_id': order.logistics_tracking_id,  # ← SOLO ESTE
                    'items': []
                }
                
                # Si tenemos datos del envío, agregar info extra
                if datos_envio:
                    order_data['tracking_number'] = datos_envio.get('tracking_number')
                    order_data['estimated_delivery'] = datos_envio.get('estimated_delivery_at')
                    order_data['shipping_cost'] = datos_envio.get('total_cost')
                    order_data['shipping_currency'] = datos_envio.get('currency')
                
                # Procesar items
                for item in order.items.all():
                    producto_info = obtener_info_producto_para_orden(request, item.productId)
                    
                    if not producto_info:
                        producto_info = {
                            'id': item.productId,
                            'name': f'Producto {item.productId}',
                            'price': float(item.price),
                            'description': ''
                        }
                    
                    subtotal = item.quantity * float(item.price)
                    
                    order_data['items'].append({
                        'productId': item.productId,
                        'quantity': item.quantity,
                        'subtotal': subtotal,
                        'product': producto_info
                    })
                
                orders_data.append(order_data)
                print(f"✅ Orden #{order.id} procesada - Estado: {order.status}")
                
        except Exception as e:
            print(f"❌ Error en orders_view: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"📊 Total de órdenes a mostrar: {len(orders_data)}")
    return render(request, 'portal_compras/ordenes.html', {
        'orders': orders_data,
        'user': request.user if request.user.is_authenticated else None
    })

def lista_productos(request):
    """Vista de lista de productos - funciona para usuarios autenticados y no autenticados"""
    productos = []
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')

    try:
        # Si el usuario está autenticado, usar su token
        if request.user.is_authenticated:
            try:
                social_auth = request.user.social_auth.get(provider='keycloak')
                access_token = social_auth.extra_data['access_token']
                
                print(f"🔄 Usando token de usuario: {request.user.username}")
                
                stock_url = "https://stock.mmalgor.com.ar/v1/productos"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                print(f"🔄 Llamando a Stock API con token de usuario...")
                response = requests.get(stock_url, headers=headers, timeout=10)
                
            except Exception as e:
                print(f"❌ Error con token de usuario: {e}")
                # Si falla el token del usuario, intentar con client credentials
                access_token = None
        else:
            # Usuario no autenticado - usar client credentials
            access_token = None
        
        # Si no hay token de usuario (no autenticado o falló), usar client credentials
        if not access_token:
            from .keycloak_auth import obtener_token_client_credentials
            access_token = obtener_token_client_credentials()
            
            if not access_token:
                print("❌ No se pudo obtener token para productos")
                productos = get_productos_prueba("No se pudo autenticar con Stock API")
            else:
                stock_url = "https://stock.mmalgor.com.ar/v1/productos"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                print(f"🔄 Llamando a Stock API con client credentials...")
                response = requests.get(stock_url, headers=headers, timeout=10)
        
        # Procesar respuesta si tenemos token
        if access_token and response.status_code == 200:
            productos_api = response.json()
            print(f"✅ {len(productos_api)} productos obtenidos del Stock")
            
            for producto in productos_api:
                categoria_principal = 'General'
                if producto.get('categorias') and len(producto['categorias']) > 0:
                    categoria_principal = producto['categorias'][0].get('nombre', 'General')
                
                imagen_principal = None
                if producto.get('imagenes') and len(producto['imagenes']) > 0:
                    for img in producto['imagenes']:
                        if img.get('esPrincipal'):
                            imagen_principal = img.get('url')
                            break
                    if not imagen_principal:
                        imagen_principal = producto['imagenes'][0].get('url')
                
                productos.append({
                    'id': producto.get('id'),
                    'name': producto.get('nombre'),
                    'description': producto.get('descripcion'), 
                    'price': float(producto.get('precio', 0)),
                    'stock': producto.get('stockDisponible', 0),
                    'category': categoria_principal,
                    'imagen_url': imagen_principal,
                    'ubicacion_ciudad': producto.get('ubicacion', {}).get('ciudad', ''),
                    'ubicacion_provincia': producto.get('ubicacion', {}).get('provincia', ''),
                })
        
        elif access_token and response.status_code != 200:
            print(f"❌ Error Stock API: {response.status_code} - {response.text}")
            productos = get_productos_prueba(f"Error API: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error general obteniendo productos: {e}")
        import traceback
        traceback.print_exc()
        productos = get_productos_prueba(f"Error: {str(e)}")
    
    # Aplicar filtros
    if query:
        productos = [p for p in productos if query.lower() in p.get('name', '').lower()]
    
    if categoria:
        productos = [p for p in productos if p.get('category', '').lower() == categoria.lower()]
    
    categorias = sorted(list(set([p.get('category', '') for p in productos if p.get('category')])))
    
    print(f"📦 Enviando {len(productos)} productos al template - Usuario: {'Autenticado' if request.user.is_authenticated else 'No autenticado'}")
    
    return render(request, 'portal_compras/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': categoria,
        'user': request.user if request.user.is_authenticated else None
    })

# =============================================================================
# VISTAS DE PERFIL Y ERROR
# =============================================================================

@login_required
def profile_view(request):
    """Vista del perfil de usuario"""
    user = request.user
    profile_data = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
    }
    
    is_keycloak_user = False
    if hasattr(user, 'social_auth'):
        social_auth = user.social_auth.filter(provider='keycloak')
        if social_auth.exists():
            is_keycloak_user = True
    
    return render(request, 'portal_compras/profile.html', {
        'profile': profile_data,
        'is_keycloak_user': is_keycloak_user,
        'user': user
    })

def login_error_view(request):
    """Vista para mostrar errores de autenticación"""
    return render(request, 'portal_compras/login_error.html', {
        'user': request.user if request.user.is_authenticated else None
    })

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def get_user_cart(user):
    """Método seguro para obtener o crear el carrito del usuario"""
    from .models import ShoppingCart
    try:
        return ShoppingCart.objects.get(user=user)
    except ShoppingCart.DoesNotExist:
        return ShoppingCart.objects.create(user=user, items=[], total=0)

def obtener_token_usuario(request):
    """Obtener el token de acceso del usuario autenticado"""
    if not request.user.is_authenticated:
        return None
    
    try:
        social_auth = request.user.social_auth.get(provider='keycloak')
        access_token = social_auth.extra_data.get('access_token')
        
        if access_token:
            print(f"✅ Token obtenido para usuario: {request.user.username}")
            return access_token
        else:
            print(f"❌ Usuario {request.user.username} no tiene token en social_auth")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo token de usuario {request.user.username}: {e}")
        return None

def obtener_info_producto_para_orden(request, producto_id):
    """Obtener información real del producto para mostrar en órdenes"""
    print(f"🔍 obtener_info_producto_para_orden - ID: {producto_id}")
    
    try:
        # Obtener token del usuario
        access_token = obtener_token_usuario(request)
        print(f"🔍 Token obtenido: {bool(access_token)}")
        
        if not access_token:
            print(f"❌ No se pudo obtener token para producto {producto_id}")
            return None
        
        stock_url = f"https://stock.mmalgor.com.ar/v1/productos/{producto_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🔍 Consultando: {stock_url}")
        response = requests.get(stock_url, headers=headers, timeout=10)
        print(f"🔍 Respuesta API: {response.status_code}")
        
        if response.status_code == 200:
            producto_data = response.json()
            print(f"✅ Producto obtenido: {producto_data.get('nombre', 'Sin nombre')}")
            
            imagen_principal = None
            if producto_data.get('imagenes') and len(producto_data['imagenes']) > 0:
                for img in producto_data['imagenes']:
                    if img.get('esPrincipal'):
                        imagen_principal = img.get('url')
                        break
                if not imagen_principal:
                    imagen_principal = producto_data['imagenes'][0].get('url')
            
            nombre = producto_data.get('nombre', f'Producto {producto_id}')
            print(f"🔍 Nombre extraído: {nombre}")
            
            return {
                'id': producto_data.get('id'),
                'name': nombre,
                'price': float(producto_data.get('precio', 0)),
                'description': producto_data.get('descripcion', ''),
                'imagen_url': imagen_principal
            }
        else:
            print(f"❌ Error API Stock: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo producto {producto_id}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
def get_productos_prueba(mensaje_error=""):
    """Productos de prueba si falla la API"""
    return [{
        'id': 999,
        'name': f'Modo Prueba - {mensaje_error}',
        'description': 'No se pudo conectar al servicio Stock. Revisa que el client_secret de grupo-05 sea correcto.',
        'price': 0.00,
        'stock': 0,
        'category': 'General',
        'imagen_url': 'https://via.placeholder.com/300x200/ff9900/ffffff?text=Modo+Prueba',
        'ubicacion_ciudad': 'Resistencia',
        'ubicacion_provincia': 'Chaco'
    }]

# =============================================================================
# API ENDPOINTS PROTEGIDOS CON KEYCLOAK - COMPRAS
# =============================================================================

from .keycloak_auth import keycloak_login_required

@keycloak_login_required
def api_obtener_carrito(request):
    """API protegida: Obtener carrito SOLO del usuario actual"""
    try:
        carrito = get_user_cart(request.user)
        
        carrito_data = {
            "items": carrito.items,
            "total": carrito.calculate_total(),
            "cantidad_items": len(carrito.items)
        }
        
        return JsonResponse({
            "status": "success",
            "cliente": KEYCLOAK_CLIENT_ID,
            "carrito": carrito_data
        })
        
    except Exception as e:
        return JsonResponse({
            "error": f"Error al obtener carrito: {str(e)}"
        }, status=500)

# En views.py - REEMPLAZA la función completa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_agregar_al_carrito(request):
    """API protegida: Agregar producto al carrito SOLO del usuario actual"""
    if request.method == 'POST':
        try:
            # Usar request.data (DRF ya parseó el JSON)
            data = request.data
            
            # Aceptar ambos formatos: inglés (productId) y español (producto_id)
            producto_id = data.get('productId') or data.get('producto_id')
            cantidad = data.get('quantity') or data.get('cantidad', 1)
            
            print(f"🔔 Producto ID recibido: {producto_id}")
            print(f"🔔 Cantidad recibida: {cantidad}")
            
            if not producto_id:
                return JsonResponse({
                    "error": "producto_id es requerido",
                    "message": "Debe enviar 'productId' o 'producto_id' en el cuerpo JSON"
                }, status=400)
            
            carrito = get_user_cart(request.user)
            
            # Obtener información del producto
            producto_info = obtener_info_producto_para_orden(request, producto_id)
            
            # Si no se pudo obtener, usar datos básicos
            if not producto_info:
                producto_info = {
                    'id': producto_id,
                    'nombre': f'Producto {producto_id}',
                    'precio': 0.0,
                    'descripcion': 'Información no disponible',
                    'imagenes': []
                }
            
            producto_existente = None
            for i, item in enumerate(carrito.items):
                if item.get('producto_id') == producto_id or item.get('productId') == producto_id:
                    producto_existente = i
                    break
            
            if producto_existente is not None:
                carrito.items[producto_existente]['cantidad'] += cantidad
            else:
                carrito.items.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'producto': {
                        'id': producto_id,
                        'name': producto_info.get('nombre', f'Producto {producto_id}'),
                        'price': float(producto_info.get('precio', 0)),
                        'description': producto_info.get('descripcion', ''),
                        'imagen_url': producto_info.get('imagenes', [{}])[0].get('url', '') if producto_info.get('imagenes') else ''
                    }
                })
            
            carrito.save()
            carrito.calculate_total()
            
            return JsonResponse({
                "status": "success",
                "message": "Producto agregado al carrito",
                "producto_id": producto_id,
                "cantidad": cantidad,
                "carrito": {
                    "items": carrito.items,
                    "total": float(carrito.total),
                    "cantidad_items": len(carrito.items)
                }
            })
            
        except Exception as e:
            print(f"❌ Error al agregar al carrito: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                "error": f"Error al agregar al carrito: {str(e)}"
            }, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)
def obtener_info_producto_para_orden(request, producto_id):
    """Obtener información real del producto para mostrar en órdenes y carrito"""
    try:
        # Obtener token del usuario
        access_token = obtener_token_usuario(request)
        if not access_token:
            print(f"❌ No se pudo obtener token para producto {producto_id}")
            return None
        
        stock_url = f"https://stock.mmalgor.com.ar/v1/productos/{producto_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(stock_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            producto_data = response.json()
            
            # Extraer categoría principal
            categoria_principal = 'General'
            if producto_data.get('categorias') and len(producto_data['categorias']) > 0:
                categoria_principal = producto_data['categorias'][0].get('nombre', 'General')
            
            # Extraer imagen principal
            imagen_principal = None
            if producto_data.get('imagenes') and len(producto_data['imagenes']) > 0:
                for img in producto_data['imagenes']:
                    if img.get('esPrincipal'):
                        imagen_principal = img.get('url')
                        break
                if not imagen_principal:
                    imagen_principal = producto_data['imagenes'][0].get('url')
            
            return {
                'id': producto_data.get('id'),
                'nombre': producto_data.get('nombre'),
                'precio': float(producto_data.get('precio', 0)),
                'descripcion': producto_data.get('descripcion', ''),
                'categoria': categoria_principal,
                'imagenes': producto_data.get('imagenes', []),
                'imagen_url': imagen_principal,
                'stock': producto_data.get('stockDisponible', 0)
            }
        else:
            print(f"❌ Error API Stock para producto {producto_id}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo producto {producto_id}: {e}")
        return None

# # Añade esta función auxiliar en views.py
# def obtener_info_producto_para_orden_con_token(access_token, producto_id):
#     """Obtener información del producto usando un token específico"""
#     try:
#         stock_url = f"https://stock.mmalgor.com.ar/v1/productos/{producto_id}"
#         headers = {
#             'Authorization': f'Bearer {access_token}',
#             'Content-Type': 'application/json'
#         }
        
#         response = requests.get(stock_url, headers=headers, timeout=10)
        
#         if response.status_code == 200:
#             producto_data = response.json()
            
#             imagen_principal = None
#             if producto_data.get('imagenes') and len(producto_data['imagenes']) > 0:
#                 for img in producto_data['imagenes']:
#                     if img.get('esPrincipal'):
#                         imagen_principal = img.get('url')
#                         break
#                 if not imagen_principal:
#                     imagen_principal = producto_data['imagenes'][0].get('url')
            
#             return {
#                 'id': producto_data.get('id'),
#                 'nombre': producto_data.get('nombre'),
#                 'precio': float(producto_data.get('precio', 0)),
#                 'descripcion': producto_data.get('descripcion', ''),
#                 'imagenes': producto_data.get('imagenes', [])
#             }
#         else:
#             print(f"❌ Error API Stock para producto {producto_id}: {response.status_code}")
#             return None
            
#     except Exception as e:
#         print(f"❌ Error obteniendo producto: {e}")
#         return None

@keycloak_login_required
def api_limpiar_carrito(request):
    """API protegida: Vaciar carrito"""
    try:
        from .models import ShoppingCart
        
        carrito, created = ShoppingCart.objects.get_or_create(user=request.user)
        carrito.items = []
        carrito.save()
        
        return JsonResponse({
            "status": "success",
            "message": "Carrito vaciado",
            "cliente": KEYCLOAK_CLIENT_ID
        })
        
    except Exception as e:
        return JsonResponse({
            "error": f"Error al limpiar carrito: {str(e)}"
        }, status=500)

@keycloak_login_required
def api_crear_orden_compra(request):
    """API protegida: Crear una nueva orden de compra"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            items = data.get('items', [])
            if not items:
                return JsonResponse({
                    "error": "La orden debe contener items"
                }, status=400)
            
            from .models import Order, OrderItem
            
            orden = Order.objects.create(
                user=request.user,
                total=data.get('total', 0),
                delivery_address=data.get('delivery_address', ''),
                payment_method=data.get('payment_method', 'TARJETA'),
                status='PENDIENTE'
            )
            
            for item in items:
                OrderItem.objects.create(
                    order=orden,
                    productId=item.get('producto_id'),
                    quantity=item.get('cantidad', 1),
                    price=item.get('precio', 0)
                )
            
            return JsonResponse({
                "status": "success",
                "orden_id": orden.id,
                "message": "Orden creada exitosamente",
                "cliente": KEYCLOAK_CLIENT_ID
            })
            
        except Exception as e:
            return JsonResponse({
                "error": f"Error al crear orden: {str(e)}"
            }, status=500)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@keycloak_login_required
def api_obtener_ordenes_usuario(request):
    """API protegida: Obtener órdenes SOLO del usuario actual"""
    try:
        from .models import Order
        
        ordenes = Order.objects.filter(user=request.user).order_by('-date')
        
        ordenes_data = []
        for orden in ordenes:
            orden_data = {
                "id": orden.id,
                "fecha": orden.date.isoformat(),
                "total": float(orden.total),
                "estado": orden.status,
                "direccion_entrega": orden.delivery_address,
                "metodo_pago": orden.payment_method,
                "items": []
            }
            
            for item in orden.items.all():
                orden_data['items'].append({
                    "producto_id": item.productId,
                    "cantidad": item.quantity,
                    "precio": float(item.price),
                    "subtotal": float(item.quantity * item.price)
                })
            
            ordenes_data.append(orden_data)
        
        return JsonResponse({
            "status": "success",
            "cliente": KEYCLOAK_CLIENT_ID,
            "total_ordenes": len(ordenes_data),
            "ordenes": ordenes_data
        })
        
    except Exception as e:
        return JsonResponse({
            "error": f"Error al obtener órdenes: {str(e)}"
        }, status=500)

# =============================================================================
# INTEGRACIÓN CON API EXTERNA DE STOCK
# =============================================================================

@keycloak_login_required
def productos_stock(request):
    """API protegida: Proxy para productos del equipo Stock"""
    try:
        response = requests.get("https://stock.mmalgor.com.ar/v1/productos", timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                "status": "success",
                "source": "stock-api",
                "client": KEYCLOAK_CLIENT_ID,
                "data": response.json()
            })
        else:
            return JsonResponse({
                "status": "error", 
                "message": f"Stock API responded with status {response.status_code}"
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error connecting to Stock API: {str(e)}"
        }, status=500)

@keycloak_login_required  
def producto_detalle(request, producto_id):
    """API protegida: Producto específico del Stock"""
    try:
        response = requests.get(f"https://stock.mmalgor.com.ar/v1/productos/{producto_id}", timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                "status": "success",
                "data": response.json()
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": f"Producto {producto_id} no encontrado"
            }, status=404)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error connecting to Stock API: {str(e)}"
        }, status=500)

# =============================================================================
# TEST Y DEBUG
# =============================================================================

def test_keycloak(request):
    """Test para verificar que Keycloak funciona"""
    try:
        from keycloak import KeycloakOpenID
        
        keycloak_openid = KeycloakOpenID(
            server_url=KEYCLOAK_SERVER_URL,
            client_id=KEYCLOAK_CLIENT_ID,
            realm_name=KEYCLOAK_REALM,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        
        token = keycloak_openid.token(grant_type="client_credentials")
        return JsonResponse({
            "status": "success", 
            "message": "Keycloak integrado correctamente",
            "client_id": KEYCLOAK_CLIENT_ID,
            "token_obtenido": True
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
def obtener_display_estado(status):
    """Convertir estado interno a texto amigable para mostrar"""
    estados = {
        'PENDING': 'Pendiente',
        'PROCESSING': 'Procesando',
        'IN_TRANSIT': 'En camino',
        'DELIVERED': 'Entregado',
        'CANCELLED': 'Cancelado'
    }
    return estados.get(status, status)

def consultar_estado_envio_logistica(tracking_id):
    """
    Consultar el estado actual de un envío en la API de Logística
    Versión simplificada con manejo de errores básico
    """
    try:
        LOGI_API_URL = getattr(settings, 'LOGI_API_URL', 'https://apilogistica.mmalgor.com.ar/')
        
        # Obtener token
        token = obtener_token_logistica_client_credentials()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # Endpoint: /shipping/{id}
        url = f"{LOGI_API_URL.rstrip('/')}/shipping/{tracking_id}"
        
        # Timeout corto para no bloquear la UI
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200:
            return response.json()
        else:
            # Silenciar errores 404 (envío no encontrado) para no spamear logs
            if response.status_code != 404:
                print(f"⚠️ Error {response.status_code} consultando envío {tracking_id}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout consultando envío {tracking_id}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"🔌 Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        return None

def mapear_estado_logistica(estado_logistica):
    """
    Mapear estados de Logística API a estados internos
    """
    mapeo = {
        'CREATED': 'PROCESSING',
        'IN_TRANSIT': 'IN_TRANSIT',
        'DELIVERED': 'DELIVERED',
        'CANCELLED': 'CANCELLED',
        'FAILED': 'CANCELLED',
        'RETURNED': 'CANCELLED'
    }
    return mapeo.get(estado_logistica)

@keycloak_login_required
def envios_logistica(request):
    """API protegida: Proxy para productos del equipo Stock"""
    try:
        response = requests.get("https://apilogistica.mmalgor.com.ar", timeout=10)
        
        if response.status_code == 200:
            return JsonResponse({
                "status": "success",
                "source": "logistica-api",
                "client": KEYCLOAK_CLIENT_ID,
                "data": response.json()
            })
        else:
            return JsonResponse({
                "status": "error", 
                "message": f"Stock API responded with status {response.status_code}"
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error connecting to Stock API: {str(e)}"
        }, status=500)

def reservas_page(request):
    """Vista para mostrar las reservas/enviós del usuario"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'portal_compras/reservas.html', {
        'user': request.user
    })
def obtener_token_logistica_client_credentials():
    """
    Obtener token de acceso para la API de Logística usando client credentials
    """
    try:
        LOGI_API_URL = getattr(settings, "LOGI_API_URL", "https://apilogistica.mmalgor.com.ar/")
        CLIENT_ID = getattr(settings, "LOGI_API_CLIENT_ID", "grupo-12")
        CLIENT_SECRET = getattr(settings, "LOGI_API_CLIENT_SECRET", "")
        
        print(f"🔐 Intentando obtener token para {CLIENT_ID} en {LOGI_API_URL}")
        
        # URL de Keycloak para obtener token
        token_url = "https://keycloak.mmalgor.com.ar/realms/ds-2025-realm/protocol/openid-connect/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(token_url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"✅ Token obtenido exitosamente")
            return access_token
        else:
            print(f"❌ Error obteniendo token client_credentials: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en obtener_token_logistica_client_credentials: {e}")
        return None
